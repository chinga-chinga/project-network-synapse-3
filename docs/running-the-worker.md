# Running the Synapse Worker & Triggering Workflows

Step-by-step guide to start the Temporal worker and execute a network change workflow.

---

## Prerequisites

- GCP VM (`synapse-vm-01`) running with Docker containers up
- Infrahub seeded with schemas + device data (Module 6 of install guide)
- Containerlab SR Linux nodes running (Module 7)

---

## Step 1: Deploy the Project to the VM

> **Note:** If you want to run `NetworkChangeWorkflow` end-to-end, your worker **must** be able to reach the `172.20.20.x` Containerlab node IP addresses. Usually this means starting the worker on the GCP VM itself, or setting up Tailscale Subnet Routing to advertise the `172.20.20.0/24` network.

```bash
# SSH into the VM
gcloud compute ssh synapse-vm-01 --zone=us-central1-a

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH=$HOME/.local/bin:$PATH

# Clone the repo (skip if already cloned)
cd ~
git clone https://github.com/chinga-chinga/project-network-synapse-3.git
cd project-network-synapse-3
git submodule update --init --recursive

# Install dependencies
uv sync --all-groups
```

---

## Step 2: Set Environment Variables

```bash
# Create .env file (or export directly)
export TEMPORAL_ADDRESS="localhost:7233"
export INFRAHUB_URL="http://localhost:8000"
export INFRAHUB_TOKEN=""  # Set this after getting a token from Infrahub UI
```

---

## Step 3: Start the Synapse Worker

```bash
cd ~/project-network-synapse-3

# Option A: Run in foreground (for debugging)
uv run python -m synapse_workers.worker

# Option B: Run in background
nohup uv run python -m synapse_workers.worker > /tmp/synapse-worker.log 2>&1 &
echo "Worker PID: $!"

# Check logs
tail -f /tmp/synapse-worker.log
```

You should see:  
`Worker connected to localhost:7233, listening on queue 'network-changes'`

---

## Step 4: Verify Worker in Temporal UI

1. Open Temporal UI: `http://<VM_IP>:8080`
2. Navigate to **Workers** → **network-changes** task queue
3. You should see 1 active worker with 3 registered workflows:
   - `NetworkChangeWorkflow`
   - `DriftRemediationWorkflow`
   - `EmergencyChangeWorkflow`

---

## Step 5: Trigger a Test Workflow

```bash
# From the VM (or any machine with temporalio installed):
cd ~/project-network-synapse-3

uv run python -c "
import asyncio
from temporalio.client import Client

async def main():
    client = await Client.connect('localhost:7233')
    result = await client.execute_workflow(
        'NetworkChangeWorkflow',
        args=['spine01', '172.20.20.10'],
        id='demo-network-change-001',
        task_queue='network-changes',
    )
    print(f'Workflow result: {result}')

asyncio.run(main())
"
```

---

## Step 6: Watch the Workflow Execute

1. Open Temporal UI: `http://<VM_IP>:8080`
2. Click on workflow `demo-network-change-001`
3. Watch the 7 steps execute in real time:
   - ✅ Step 1: Backup running config (gNMI GET)
   - ✅ Step 2: Fetch intended config (Infrahub GraphQL)
   - ✅ Step 3: Generate SR Linux JSON
   - ✅ Step 4: Hygiene check (pre-deployment gate)
   - ✅ Step 5: Deploy config (gNMI SET)
   - ✅ Step 6: Validate BGP (gNMI GET operational state)
   - ✅ Step 7: Update device status in Infrahub

---

## Troubleshooting

| Issue                            | Fix                                                                                                                     |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Worker can't connect to Temporal | Check `TEMPORAL_ADDRESS`. Verify Temporal is running: `docker ps \| grep temporal`                                      |
| `fetch_device_config` fails      | Set `INFRAHUB_URL` and `INFRAHUB_TOKEN`. Check Infrahub is healthy: `curl http://localhost:8000`                        |
| `backup_running_config` fails    | Check Containerlab nodes are running: `sudo containerlab inspect`                                                       |
| `deploy_config` times out        | Verify gNMI port 57400 is accessible on the SR Linux node                                                               |
| BGP validation fails             | BGP may not be configured yet. Check: `ssh admin@172.20.20.10` → `show network-instance default protocols bgp neighbor` |

---

## Stopping the Worker

```bash
# If running in foreground: Ctrl+C

# If running in background:
pkill -f "synapse_workers.worker"
```
