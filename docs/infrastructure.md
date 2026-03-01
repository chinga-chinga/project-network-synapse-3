# Infrastructure Connection Guide

This document covers how to connect to all services running on the GCP VMs (production and staging).

## VM Overview

| Property | Production | Staging |
|----------|-----------|---------|
| **VM Name** | `synapse-vm-01` | `synapse-staging-vm` |
| **Machine Type** | e2-standard-4 (4 vCPU, 16GB) | e2-standard-4 (4 vCPU, 16GB) |
| **OS** | Debian 12 | Debian 12 |
| **Zone** | us-central1-a | us-central1-a |
| **GCP Project** | `project-network-synapse` | `project-network-synapse` |
| **Repo Path** | `/home/anton/project-network-synapse-3` | `/home/anton/project-network-synapse-3` |
| **Branch** | `main` | `develop` |
| **Services** | Infrahub, Temporal, Containerlab, synapse-worker | Infrahub, Temporal, Containerlab, synapse-worker |

> **Note:** Both VMs run identical service stacks. The staging VM tracks the `develop` branch
> for pre-production validation. The sections below (Containerlab, Infrahub, Temporal, etc.)
> apply to both VMs — substitute the VM name in SSH/gcloud commands as appropriate.
> For staging local access, use the staging tunnel ports (9000, 9080, 59080) shown below.

---

## Production VM — synapse-vm-01

### VM Access

**GCP VM:** `synapse-vm-01` (e2-standard-4, us-central1-a, Debian 12, 16GB RAM)

```bash
# SSH via gcloud
gcloud compute ssh synapse-vm-01 --zone=us-central1-a

# Tailscale IP (if Tailscale is connected)
# VM: 100.123.70.8
```

### All-in-One SSH Tunnel

Forward all web UIs to your laptop in a single command:

```bash
gcloud compute ssh synapse-vm-01 --zone=us-central1-a -- \
  -L 8000:localhost:8000 \
  -L 8080:localhost:8080 \
  -L 50080:localhost:50080
```

Then open:

| Service | Local URL |
|---------|-----------|
| Infrahub UI | http://localhost:8000 |
| Temporal UI | http://localhost:8080 |
| Containerlab Graph | http://localhost:50080 |

---

## Staging VM — synapse-staging-vm

**GCP VM:** `synapse-staging-vm` (e2-standard-4, us-central1-a, Debian 12, 16GB RAM)

**Branch:** `develop` (auto-deployed on push to `develop`)

### VM Access

```bash
# SSH via gcloud
gcloud compute ssh synapse-staging-vm --zone=us-central1-a
```

### All-in-One SSH Tunnel

Forward all web UIs to your laptop in a single command:

```bash
gcloud compute ssh synapse-staging-vm --zone=us-central1-a -- \
  -L 9000:localhost:8000 \
  -L 9080:localhost:8080 \
  -L 59080:localhost:50080
```

Then open:

| Service | Local URL |
|---------|-----------|
| Infrahub UI | http://localhost:9000 |
| Temporal UI | http://localhost:9080 |
| Containerlab Graph | http://localhost:59080 |

> **Tip:** Staging uses different local ports (9000, 9080, 59080) so you can tunnel to both
> production and staging simultaneously without port conflicts.

---

## Containerlab (Nokia SR Linux)

### Topology

Spine-leaf topology with 1 spine and 2 leaf switches, all Nokia SR Linux.

| Device | Role | Type | Management IP | Container Name |
|--------|------|------|---------------|----------------|
| spine01 | spine | 7220 IXR-D3 | 172.20.20.3 | clab-spine-leaf-lab-spine01 |
| leaf01 | leaf | 7220 IXR-D2 | 172.20.20.2 | clab-spine-leaf-lab-leaf01 |
| leaf02 | leaf | 7220 IXR-D2 | 172.20.20.4 | clab-spine-leaf-lab-leaf02 |

### Credentials

| Protocol | Username | Password |
|----------|----------|----------|
| SSH / JSON-RPC / gNMI | `admin` | `NokiaSrl1!` |

### Connecting to Devices

All device access is from **within the VM** (the 172.20.20.0/24 management network is internal to the VM).

```bash
# SSH into the VM first
gcloud compute ssh synapse-vm-01 --zone=us-central1-a

# SSH into a device
ssh admin@172.20.20.3          # spine01
ssh admin@172.20.20.2          # leaf01
ssh admin@172.20.20.4          # leaf02
```

### JSON-RPC (HTTPS, port 443)

```bash
# From the VM
curl -sk https://172.20.20.3/jsonrpc -u admin:NokiaSrl1! \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "get",
    "params": {
      "commands": [
        {"path": "/system/information"}
      ]
    }
  }'
```

### gNMI (port 57400)

```bash
# From the VM — using pygnmi or similar
# Target: 172.20.20.3:57400 (spine01)
# TLS: insecure (self-signed cert)
```

### Containerlab CLI

```bash
# Inspect running topology
sudo containerlab inspect -t ~/containerlab/topology.clab.yml

# Interactive topology graph (web UI on port 50080)
sudo containerlab graph -t ~/containerlab/topology.clab.yml

# Destroy and redeploy
sudo containerlab destroy -t ~/containerlab/topology.clab.yml
sudo containerlab deploy -t ~/containerlab/topology.clab.yml
```

### Topology Diagram

```
             ┌──────────┐
             │  spine01  │
             │ IXR-D3   │
             │ .3       │
             └─┬──┬─┬──┬┘
          e1-1 │  │ │  │ e1-4
               │  │ │  │
          e1-49│  │ │  │e1-49
             ┌─┴──┘ └──┴─┐
             │            │
         ┌───┴───┐   ┌───┴───┐
         │ leaf01 │   │ leaf02 │
         │ IXR-D2 │   │ IXR-D2 │
         │ .2     │   │ .4     │
         └────────┘   └────────┘

Links:
  spine01:e1-1 <-> leaf01:e1-49
  spine01:e1-2 <-> leaf02:e1-49
  spine01:e1-3 <-> leaf01:e1-50
  spine01:e1-4 <-> leaf02:e1-50

Management: 172.20.20.0/24
```

### Accessing Lab Nodes from Your Laptop

The 172.20.20.0/24 network is internal to the VM. Options to reach it from your laptop:

**Option 1: Tailscale Subnet Router (recommended)**
```bash
# On the VM
sudo tailscale up --advertise-routes=172.20.20.0/24
```
Then approve the route in your Tailscale admin console. After that, you can SSH/curl directly to 172.20.20.x from your laptop.

**Option 2: SSH Jump Host**
```bash
# From your laptop — SSH through the VM
ssh -J synapse-vm-01 admin@172.20.20.3
```

**Option 3: SOCKS Proxy**
```bash
# Start a SOCKS proxy through the VM
gcloud compute ssh synapse-vm-01 --zone=us-central1-a -- -D 1080

# Then configure your browser/tools to use SOCKS5 proxy on localhost:1080
```

---

## Infrahub (Source of Truth)

### Connection Details

| Interface | URL | Notes |
|-----------|-----|-------|
| Web UI | http://localhost:8000 | Via SSH tunnel |
| GraphQL Playground | http://localhost:8000/graphql | Interactive query editor |
| REST API | http://localhost:8000/api/ | Schema management |

### Credentials

| Username | Password |
|----------|----------|
| `admin` | `infrahub` |

### Accessing the UI

```bash
# Start SSH tunnel
gcloud compute ssh synapse-vm-01 --zone=us-central1-a -- -L 8000:localhost:8000

# Open in browser
open http://localhost:8000
```

### GraphQL API

```bash
# Get an auth token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "infrahub"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Query all devices
curl -s -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "{ DcimDevice { edges { node { display_label management_ip { value } role { value } } } } }"
  }' | python3 -m json.tool

# Query BGP sessions
curl -s -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "{ RoutingBGPSession { edges { node { display_label description { value } session_type { value } } } } }"
  }' | python3 -m json.tool
```

### Python SDK

```python
from infrahub_sdk import InfrahubClient

async def main():
    client = await InfrahubClient.init(
        address="http://localhost:8000",
        # token="<optional-api-token>"
    )

    # Query devices
    devices = await client.all("DcimDevice")
    for device in devices:
        print(f"{device.name.value} - {device.management_ip.value}")
```

### Loaded Schemas

The following schema extensions are loaded (in dependency order):

1. **Base schemas** (pre-loaded): DcimDevice, InterfacePhysical, IpamIPAddress, LocationSite, etc.
2. **VRF extension**: IpamVRF, IpamRouteTarget
3. **Routing base**: RoutingProtocol (generic)
4. **Routing BGP**: RoutingAutonomousSystem, RoutingBGPPeerGroup, RoutingBGPSession
5. **Custom device extension**: management_ip, lab_node_name, asn (on DcimDevice)
6. **Custom interface extension**: role dropdown (on InterfacePhysical)

See [schemas.md](schemas.md) for full schema architecture details.

### Seed Data

The Infrahub instance is pre-populated with:

| Object Type | Count | Details |
|-------------|-------|---------|
| Devices | 3 | spine01, leaf01, leaf02 |
| Interfaces | 11 | 4x spine fabric + loopback, 2x per leaf fabric + loopback |
| IP Addresses | 11 | /31 fabric links + /32 loopbacks |
| Autonomous Systems | 3 | AS65000 (spine), AS65001 (leaf01), AS65002 (leaf02) |
| BGP Sessions | 4 | eBGP underlay on all fabric links |
| VRFs | 1 | default |

See [seed-data.md](seed-data.md) for the full IP addressing plan.

### Docker Containers

```bash
# Check Infrahub container status (from VM)
docker ps --filter "name=infrahub"

# View logs
docker compose -p infrahub logs -f infrahub-server

# Restart
docker compose -p infrahub restart
```

---

## Temporal (Workflow Orchestration)

### Connection Details

| Interface | URL / Address | Notes |
|-----------|---------------|-------|
| Web UI | http://localhost:8080 | Via SSH tunnel |
| gRPC | localhost:7233 | Worker/client connections |
| Namespace | `default` | Primary namespace |
| Task Queue | `network-changes` | Project task queue |

### Accessing the UI

```bash
# Start SSH tunnel
gcloud compute ssh synapse-vm-01 --zone=us-central1-a -- -L 8080:localhost:8080

# Open in browser
open http://localhost:8080
```

### Python SDK

```python
import asyncio
from datetime import timedelta

from temporalio.client import Client
from temporalio.worker import Worker

async def main():
    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Execute a workflow
    result = await client.execute_workflow(
        "MyWorkflow",
        id="my-workflow-id",
        task_queue="network-changes",
    )
    print(f"Result: {result}")
```

### Worker Setup

```python
from temporalio.worker import Worker

async with Worker(
    client,
    task_queue="network-changes",
    workflows=[MyWorkflow],
    activities=[my_activity],
):
    print("Worker running... press Ctrl+C to stop")
    await asyncio.Future()  # run forever
```

### Environment Variable

The worker reads the Temporal address from an environment variable:

```bash
export TEMPORAL_ADDRESS="localhost:7233"  # default
```

### Docker Containers

```bash
# Check Temporal container status (from VM)
docker ps --filter "name=temporal"

# View logs
docker compose -p temporal logs -f temporal

# Temporal CLI (via admin-tools container)
docker exec temporal temporal operator namespace list
docker exec temporal temporal operator cluster health
```

---

## Port Reference

All services listen on `localhost` inside the VM. Use SSH tunnels for external access.

| Port | Service | Protocol |
|------|---------|----------|
| 8000 | Infrahub Web UI + API | HTTP |
| 8080 | Temporal Web UI | HTTP |
| 7233 | Temporal gRPC | gRPC |
| 443 | SR Linux JSON-RPC (per device) | HTTPS |
| 57400 | SR Linux gNMI (per device) | gRPC/TLS |
| 50080 | Containerlab Graph UI | HTTP |
| 6379 | Redis (Infrahub cache) | TCP |
| 2004 | Neo4j (Infrahub database) | Bolt |
| 5432 | PostgreSQL (Temporal) | TCP |
| 9200 | Elasticsearch (Temporal) | HTTP |

---

## Troubleshooting

### Services not starting

```bash
# Check all containers
docker ps -a

# Check container logs
docker compose -p infrahub logs -f
docker compose -p temporal logs -f
```

### Containerlab nodes not reachable

```bash
# Verify nodes are running
sudo containerlab inspect -t ~/containerlab/topology.clab.yml

# Check docker networks
docker network ls | grep clab

# Ping from VM
ping -c 2 172.20.20.3
```

### SSH tunnel not working

```bash
# Ensure no local process is using the port
lsof -i :8000

# Use a different local port if needed
gcloud compute ssh synapse-vm-01 --zone=us-central1-a -- -L 9000:localhost:8000
# Then access via http://localhost:9000
```

### Infrahub API returns 401

```bash
# Re-authenticate (tokens expire after 1 hour)
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "infrahub"}'
```
