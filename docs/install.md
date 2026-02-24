# Network Synapse — VM Installation Guide

Modular installation plan for deploying Network Synapse on a fresh GCP VM.
Each module is self-contained with prerequisites, commands, verification, and troubleshooting.
Designed for agent-driven autonomous execution.

---

## Prerequisites Summary

| Requirement     | Specification                                                    |
| --------------- | ---------------------------------------------------------------- |
| **VM**          | GCP e2-standard-4 (4 vCPU, 16GB RAM), 50GB SSD, Ubuntu 22.04 LTS |
| **Modules 1-6** | Core platform (required)                                         |
| **Module 7**    | Containerlab network lab (required for integration testing)      |
| **Module 8**    | Worker + full verification (required)                            |
| **Module 9**    | Dev tooling (required for development)                           |
| **Module 10**   | Remote access (optional)                                         |

## Module Dependency Graph

```
Module 1 (Base OS)
  └── Module 2 (Docker)
  │     └── Module 5 (Infrastructure Services)
  │           └── Module 6 (App Bootstrap)
  │           └── Module 8 (Worker + Verification)
  └── Module 3 (Python + uv)
  │     └── Module 4 (Repo + Project Setup)
  │           └── Module 5
  │           └── Module 9 (Dev Tools)
  └── Module 7 (Containerlab) [independent after Module 2]
  └── Module 10 (Remote Access) [independent after Module 1]
```

---

## Module 1: GCP VM Provisioning + Base OS

**Purpose:** Provision a GCP VM and prepare the base operating system.

**Prerequisites:** GCP project with billing enabled, `gcloud` CLI authenticated.

**Requires sudo:** Yes

**Estimated time:** 5-10 minutes

### 1.1 Provision the VM

```bash
# Create the VM (adjust project, zone, and network tags as needed)
gcloud compute instances create synapse-vm-01 \
  --project=<YOUR_PROJECT_ID> \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=synapse-vm \
  --metadata=enable-oslogin=TRUE
```

### 1.2 Create Firewall Rules

```bash
# SSH access
gcloud compute firewall-rules create allow-ssh-synapse \
  --project=<YOUR_PROJECT_ID> \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:22 \
  --target-tags=synapse-node \
  --source-ranges=<YOUR_IP>/32 \
  --description="SSH access to synapse nodes"

# Application service ports
gcloud compute firewall-rules create allow-synapse-services \
  --project=<YOUR_PROJECT_ID> \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:8000,tcp:8080,tcp:3000,tcp:9090,tcp:7474,tcp:7687,tcp:15672 \
  --target-tags=synapse-node \
  --source-ranges=<YOUR_IP>/32 \
  --description="Infrahub (8000), Temporal UI (8080), Grafana (3000), Prometheus (9090), Neo4j (7474/7687), RabbitMQ (15672)"
```

**Ports reference:**

| Port  | Service             |
| ----- | ------------------- |
| 8000  | Infrahub UI + API   |
| 8080  | Temporal UI         |
| 3000  | Grafana dashboards  |
| 9090  | Prometheus metrics  |
| 7474  | Neo4j browser       |
| 7687  | Neo4j bolt          |
| 15672 | RabbitMQ management |

> **Security note:** Replace `<YOUR_IP>/32` with your specific IP or Tailscale
> CIDR. Never use `0.0.0.0/0` for these ports in production.

### 1.3 SSH into the VM

```bash
gcloud compute ssh synapse-vm-01 --zone=us-central1-a
```

### 1.4 Base OS Setup

```bash
sudo apt-get update && sudo apt-get upgrade -y

sudo apt-get install -y \
  curl \
  wget \
  git \
  ca-certificates \
  gnupg \
  lsb-release \
  build-essential \
  software-properties-common \
  jq
```

### Verification

```bash
uname -a                    # Expect: Linux ... 5.15+ ... x86_64
git --version               # Expect: git version 2.34+
df -h /                     # Expect: 45GB+ available
free -h                     # Expect: 15GB+ total memory
nproc                       # Expect: 4
```

### Troubleshooting

| Issue                     | Fix                                                                  |
| ------------------------- | -------------------------------------------------------------------- |
| VM creation fails (quota) | Check regional quotas: `gcloud compute regions describe us-central1` |
| SSH timeout               | Verify firewall allows TCP:22, check VPC network settings            |
| apt-get fails             | `sudo apt-get update --fix-missing` then retry                       |

---

## Module 2: Docker Engine + Docker Compose

**Purpose:** Install Docker CE and Docker Compose v2 plugin.

**Prerequisites:** Module 1 complete.

**Requires sudo:** Yes

**Estimated time:** 3-5 minutes

### 2.1 Install Docker CE

```bash
# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine + Compose plugin
sudo apt-get update
sudo apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

### 2.2 Configure Docker for Non-root Usage

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group change (or log out and back in)
newgrp docker
```

### 2.3 Enable Docker on Boot

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

### Verification

```bash
docker --version            # Expect: Docker version 24+
docker compose version      # Expect: Docker Compose version v2.20+
docker run hello-world      # Expect: "Hello from Docker!" message
docker info | grep "Server" # Expect: Server Version listed
```

### Troubleshooting

| Issue                                  | Fix                                                 |
| -------------------------------------- | --------------------------------------------------- |
| `permission denied` on docker commands | Log out and back in, or run `newgrp docker`         |
| `Cannot connect to the Docker daemon`  | `sudo systemctl start docker`                       |
| GPG key import fails                   | Check internet connectivity, retry with `--retry 3` |

---

## Module 3: Python 3.11 + uv Package Manager

**Purpose:** Install Python 3.11 and the uv package manager.

**Prerequisites:** Module 1 complete.

**Requires sudo:** Yes (for Python), No (for uv)

**Estimated time:** 3-5 minutes

### 3.1 Install Python 3.11

```bash
# Add deadsnakes PPA for Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update

# Install Python 3.11 with dev headers and venv
sudo apt-get install -y \
  python3.11 \
  python3.11-dev \
  python3.11-venv \
  python3.11-distutils
```

### 3.2 Install uv

```bash
# Install uv (Astral's Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for current session
source $HOME/.cargo/env 2>/dev/null || source $HOME/.local/bin/env 2>/dev/null

# Verify uv is in PATH
which uv
```

### Verification

```bash
python3.11 --version        # Expect: Python 3.11.x
uv --version                # Expect: uv 0.5+ (or latest)
uv python list | grep 3.11  # Expect: Python 3.11 listed
```

### Troubleshooting

| Issue                                         | Fix                                                                                       |
| --------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `add-apt-repository: command not found`       | `sudo apt-get install -y software-properties-common`                                      |
| `python3.11: command not found` after install | `sudo update-alternatives --install /usr/bin/python3.11 python3.11 /usr/bin/python3.11 1` |
| uv not in PATH after install                  | Add to `.bashrc`: `export PATH="$HOME/.local/bin:$PATH"` then `source ~/.bashrc`          |

---

## Module 4: Repository Clone + Project Setup

**Purpose:** Clone the repository, initialize submodules, and install all Python dependencies.

**Prerequisites:** Module 1 + Module 3 complete.

**Requires sudo:** No

**Estimated time:** 3-5 minutes

### 4.1 Clone the Repository

```bash
# Clone (adjust URL if using SSH)
cd ~
git clone https://github.com/chinga-chinga/project-network-synapse-3.git
cd project-network-synapse-3
```

### 4.2 Initialize Git Submodules

```bash
git submodule update --init --recursive
```

### 4.3 Set Up Environment Variables

```bash
cp .env.example .env

# Edit .env and fill in required values:
# - INFRAHUB_TOKEN (generated after Infrahub first login in Module 6)
# - TAILSCALE_AUTH_KEY (if using Module 10)
```

### 4.4 Install Python Dependencies

```bash
# Install all dependency groups (testing, linting, typing, dev)
uv sync --all-groups
```

### 4.5 Switch to the Develop Branch

```bash
git checkout develop
git pull origin develop
```

### Verification

```bash
# Verify packages are importable
uv run python -c "import network_synapse; print('backend OK')"
uv run python -c "import synapse_workers; print('workers OK')"

# Verify invoke task runner works
uv run invoke --list

# Verify submodule is populated
ls library/schema-library/base/
# Expect: directory listing with schema YAML files

# Verify project structure
ls backend/ workers/ tests/ tasks/ dev/ development/ containerlab/
```

### Troubleshooting

| Issue                               | Fix                                                        |
| ----------------------------------- | ---------------------------------------------------------- |
| `uv sync` fails with resolver error | Delete `uv.lock` and run `uv lock && uv sync --all-groups` |
| Submodule clone fails               | Check GitHub access: `ssh -T git@github.com` or use HTTPS  |
| Import errors after install         | Ensure you ran `uv sync --all-groups` (not just `uv sync`) |
| `invoke: command not found`         | Always run via `uv run invoke`, not bare `invoke`          |

---

## Module 5: Infrastructure Services

**Purpose:** Start the infrastructure stack (Infrahub, Temporal, Neo4j, Redis, RabbitMQ)
via Docker Compose.

**Prerequisites:** Module 2 + Module 4 complete.

**Requires sudo:** No (if docker group configured in Module 2)

**Estimated time:** 5-10 minutes (includes image pulls on first run)

### 5.1 Start Infrastructure

```bash
cd ~/project-network-synapse-3

# Start infrastructure-only stack (no synapse worker)
docker compose -f development/docker-compose-deps.yml up -d
```

### 5.2 Wait for Services to Initialize

Infrahub takes 30-90 seconds to fully initialize (Neo4j must be ready first, then
Infrahub applies migrations).

```bash
# Watch container status until all are running
docker compose -f development/docker-compose-deps.yml ps

# Wait for Infrahub to respond (retry loop, up to 120 seconds)
echo "Waiting for Infrahub..."
for i in $(seq 1 24); do
  if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200\|301\|302"; then
    echo "Infrahub is ready!"
    break
  fi
  echo "  Attempt $i/24 — waiting 5s..."
  sleep 5
done
```

### 5.3 Verify All Services

```bash
# Check all containers are running
docker compose -f development/docker-compose-deps.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

### Services Reference

| Service     | Container              | Port        | Health Check                                |
| ----------- | ---------------------- | ----------- | ------------------------------------------- |
| Neo4j       | infrahub-database      | 7687, 7474  | `curl http://localhost:7474`                |
| Redis       | infrahub-cache         | 6379        | `docker exec <id> redis-cli ping`           |
| RabbitMQ    | infrahub-message-queue | 5672, 15672 | `curl http://localhost:15672` (guest/guest) |
| Infrahub    | infrahub-server        | 8000        | `curl http://localhost:8000`                |
| Temporal    | temporal               | 7233        | `curl http://localhost:8080` (via UI)       |
| Temporal UI | temporal-ui            | 8080        | `curl http://localhost:8080`                |

### Verification

```bash
# All 6 containers running
docker compose -f development/docker-compose-deps.yml ps | grep -c "running"
# Expect: 6

# Infrahub API responds
curl -s http://localhost:8000 | head -c 200
# Expect: HTML or JSON response (not connection refused)

# Temporal UI responds
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
# Expect: 200

# Neo4j browser responds
curl -s -o /dev/null -w "%{http_code}" http://localhost:7474
# Expect: 200

# RabbitMQ management responds
curl -s -o /dev/null -w "%{http_code}" http://localhost:15672
# Expect: 200
```

### Troubleshooting

| Issue                                             | Fix                                                                                                |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Infrahub image pull fails (`registry.opsmill.io`) | May need `docker login registry.opsmill.io` — check Infrahub docs for registry access              |
| Neo4j OOM killed                                  | Increase VM RAM or set `NEO4J_server_memory_heap_max__size=1G` in compose environment              |
| Port conflict (address already in use)            | Check: `sudo lsof -i :<PORT>`. Override port in `.env` (e.g., `INFRAHUB_PORT=8001`)                |
| Infrahub stuck starting                           | Check logs: `docker compose -f development/docker-compose-deps.yml logs infrahub-server --tail 50` |
| RabbitMQ not ready when Infrahub starts           | Restart Infrahub: `docker compose -f development/docker-compose-deps.yml restart infrahub-server`  |

---

## Module 6: Application Bootstrap (Schemas + Data)

**Purpose:** Load Infrahub schemas, seed the network topology data, and verify the
config generation pipeline works.

**Prerequisites:** Module 5 complete (all infrastructure services running).

**Requires sudo:** No

**Estimated time:** 2-5 minutes

### 6.1 Load Schemas into Infrahub

```bash
cd ~/project-network-synapse-3

# Load custom schema extensions (DcimDevice, InterfacePhysical, BGP session)
uv run invoke backend.load-schemas
```

This loads schema YAML files from `backend/network_synapse/schemas/` into Infrahub
via the `/api/schema/load` endpoint.

### 6.2 Seed Network Topology Data

```bash
# Seed devices, interfaces, BGP sessions from seed_data.yml
uv run invoke backend.seed-data
```

This creates:

- 3 devices: spine01 (AS65000), leaf01 (AS65001), leaf02 (AS65002)
- 11 interfaces across all devices (fabric, loopback, management)
- 4 eBGP sessions (spine-to-leaf peerings)
- Organizations, locations, platforms, autonomous systems, IP prefixes

### 6.3 Test Config Generation

```bash
# Dry run — renders configs without writing files
uv run invoke backend.generate-configs --dry-run

# Full run — writes to generated-configs/<hostname>/
uv run invoke backend.generate-configs
```

### 6.4 Generate Infrahub API Token

```bash
# Open Infrahub UI in browser (or curl for token)
echo "Open http://<VM_EXTERNAL_IP>:8000 in browser"
echo "Login: admin / infrahub"
echo "Navigate to: Account Settings -> API Tokens -> Create Token"
echo "Copy the token and add it to .env as INFRAHUB_TOKEN=<token>"
```

After getting the token, update `.env`:

```bash
# Edit .env and set INFRAHUB_TOKEN
nano .env
```

### Verification

```bash
# Query Infrahub for devices (should return 3)
curl -s -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "{ DcimDevice { edges { node { hostname { value } } } } }"}' \
  | jq '.data.DcimDevice.edges | length'
# Expect: 3

# Check generated config files exist
ls generated-configs/
# Expect: spine01/ leaf01/ leaf02/ directories

ls generated-configs/spine01/
# Expect: bgp.json interfaces.json

# Validate generated JSON is parseable
cat generated-configs/spine01/bgp.json | jq . > /dev/null && echo "Valid JSON"
cat generated-configs/spine01/interfaces.json | jq . > /dev/null && echo "Valid JSON"
```

### Troubleshooting

| Issue                                      | Fix                                                                                                                                                               |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `load-schemas` fails with connection error | Verify Infrahub is running: `curl http://localhost:8000`                                                                                                          |
| `seed-data` fails with 409 conflict        | Data already exists (idempotent upserts should handle this). If persistent, restart Infrahub with fresh volumes: `docker compose down -v && docker compose up -d` |
| `generate-configs` can't connect           | Ensure `INFRAHUB_URL=http://localhost:8000` in `.env`                                                                                                             |
| GraphQL query returns empty                | Schemas not loaded — run `load-schemas` before `seed-data`                                                                                                        |

---

## Module 7: Containerlab + Nokia SR Linux Lab

**Purpose:** Install Containerlab and deploy the 3-node Nokia SR Linux spine-leaf
network topology.

**Prerequisites:** Module 2 complete (Docker running).

**Requires sudo:** Yes (containerlab requires root for network namespace operations)

**Estimated time:** 5-10 minutes (includes SR Linux image pull)

### 7.1 Install Containerlab

```bash
# Install containerlab via official installer
bash -c "$(curl -sL https://get.containerlab.dev)"
```

### 7.2 Pull Nokia SR Linux Image

```bash
# Pull the latest SR Linux image
docker pull ghcr.io/nokia/srlinux:latest
```

> **Note:** If the pull fails with auth errors, you may need to authenticate:
> `echo <GHCR_TOKEN> | docker login ghcr.io -u <USERNAME> --password-stdin`

### 7.3 Deploy the Topology

```bash
cd ~/project-network-synapse-3

# Deploy the spine-leaf lab
sudo containerlab deploy --topo containerlab/topology.clab.yml
```

This creates:

- **spine01** (Nokia SR Linux IXR-D3) — 4 fabric links
- **leaf01** (Nokia SR Linux IXR-D2) — 2 uplinks to spine
- **leaf02** (Nokia SR Linux IXR-D2) — 2 uplinks to spine
- Management network: `172.20.20.0/24` (DHCP assigned)

### 7.4 Verify Topology

```bash
# List deployed nodes
sudo containerlab inspect --topo containerlab/topology.clab.yml
```

### Fabric Links

| Link | Endpoint A   | Endpoint B   |
| ---- | ------------ | ------------ |
| 1    | spine01:e1-1 | leaf01:e1-49 |
| 2    | spine01:e1-2 | leaf02:e1-49 |
| 3    | spine01:e1-3 | leaf01:e1-50 |
| 4    | spine01:e1-4 | leaf02:e1-50 |

### Verification

```bash
# Inspect shows 3 nodes running
sudo containerlab inspect --topo containerlab/topology.clab.yml
# Expect: 3 nodes with status "running"

# SSH into spine01 (default credentials: admin / NokiaSrl1!)
ssh admin@clab-spine-leaf-lab-spine01
# At SR Linux prompt: show version
# Type: exit

# Verify all nodes are reachable
for node in spine01 leaf01 leaf02; do
  echo -n "$node: "
  docker exec clab-spine-leaf-lab-$node sr_cli "show version" 2>/dev/null | head -1 || echo "FAILED"
done
```

### Troubleshooting

| Issue                                  | Fix                                                                                                                  |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `containerlab: command not found`      | Ensure install completed: `which containerlab`. Retry install script.                                                |
| SR Linux image pull denied             | Authenticate to GHCR: `docker login ghcr.io`. The image may be public — retry without auth.                          |
| `error creating network namespace`     | Must run with `sudo`. Check kernel supports network namespaces: `ls /proc/sys/net/`                                  |
| Nodes start but links are down         | Check Docker network: `docker network ls`. Recreate: `sudo containerlab destroy ... && sudo containerlab deploy ...` |
| Not enough memory for 3 SR Linux nodes | Each node uses ~1GB RAM. Ensure VM has at least 4GB free after infrastructure services.                              |

### Cleanup

```bash
# Destroy the lab when no longer needed
sudo containerlab destroy --topo containerlab/topology.clab.yml
```

---

## Module 8: Synapse Worker + Full Stack Verification

**Purpose:** Start the Temporal worker and verify the complete platform works end-to-end.

**Prerequisites:** Module 4 + Module 5 + Module 6 complete.

**Requires sudo:** No

**Estimated time:** 3-5 minutes

### 8.1 Option A: Run Worker Locally (Recommended for Development)

```bash
cd ~/project-network-synapse-3

# Start the Temporal worker (connects to localhost:7233)
uv run invoke workers.start
```

The worker will connect to Temporal and register on the `network-changes` task queue.
Press `Ctrl+C` to stop.

### 8.2 Option B: Run Worker in Docker

```bash
cd ~/project-network-synapse-3

# Build the worker Docker image
uv run invoke dev.build

# Start the full stack (infrastructure + worker)
docker compose -f development/docker-compose.yml up -d
```

### 8.3 Run Unit Tests

```bash
# Run all unit tests (41 tests expected)
uv run invoke backend.test-unit
```

### 8.4 Run Integration Tests (if Containerlab deployed)

```bash
# Integration tests require all services + Containerlab running
uv run invoke backend.test-integration
```

### Verification

```bash
# Unit tests pass
uv run invoke backend.test-unit 2>&1 | tail -3
# Expect: "41 passed"

# Config generation works end-to-end
uv run invoke backend.generate-configs --dry-run
# Expect: BGP and interface configs rendered for all devices

# Worker is registered with Temporal (check Temporal UI)
curl -s http://localhost:8080 | head -c 100
# Expect: Temporal UI HTML response
echo ""
echo "Open http://<VM_IP>:8080 to see registered workers in Temporal UI"
```

### Troubleshooting

| Issue                             | Fix                                                                                                                                  |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Worker can't connect to Temporal  | Check: `TEMPORAL_ADDRESS=localhost:7233` in `.env`. Verify Temporal is running: `docker compose ps`                                  |
| Tests fail with import errors     | Re-run `uv sync --all-groups`                                                                                                        |
| Docker build fails                | Check Docker daemon is running. Check Dockerfile context is repo root.                                                               |
| Tests fail with connection errors | Tests mock external services — no live connections needed for unit tests. If integration tests fail, check all services are running. |

---

## Module 9: Development Tools + Quality Checks

**Purpose:** Set up pre-commit hooks, verify all quality gates pass, and prepare the
development environment.

**Prerequisites:** Module 4 complete.

**Requires sudo:** No (except Node.js install)

**Estimated time:** 3-5 minutes

### 9.1 Install Pre-commit Hooks

```bash
cd ~/project-network-synapse-3

# Install git pre-commit hooks
uv run pre-commit install
```

### 9.2 Run All Quality Checks

```bash
# Run the full quality suite (lint + security scan)
uv run invoke check-all

# Run linting specifically
uv run invoke lint

# Run YAML linting
uv run invoke docs.lint-yaml
```

### 9.3 Run Type Checking

```bash
uv run invoke backend.typecheck
```

### 9.4 Optional: Install Node.js for Markdown Linting

```bash
# Install Node.js via NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version   # Expect: v20.x
npm --version    # Expect: 10.x

# Run markdown linting
uv run invoke docs.lint-all
```

### 9.5 Run Pre-commit on All Files

```bash
# Verify pre-commit hooks work
uv run pre-commit run --all-files
```

### Verification

```bash
# Ruff lint passes
uv run ruff check . && echo "LINT OK"
# Expect: "All checks passed!" + "LINT OK"

# Ruff format passes
uv run ruff format --check . && echo "FORMAT OK"
# Expect: files listed as "already formatted" + "FORMAT OK"

# YAML lint passes
uv run yamllint . && echo "YAML OK"
# Expect: no output (clean) + "YAML OK"

# Pre-commit hooks installed
ls .git/hooks/pre-commit
# Expect: file exists
```

### Troubleshooting

| Issue                       | Fix                                                 |
| --------------------------- | --------------------------------------------------- |
| `pre-commit` not found      | Run via `uv run pre-commit`, not bare `pre-commit`  |
| Ruff fails with lint errors | Run `uv run invoke format` to auto-fix, then retry  |
| yamllint fails              | Check `.yamllint.yml` is present at repo root       |
| Node.js install fails       | Use alternative: `sudo snap install node --classic` |

---

## Module 10: Remote Access + Networking (Optional)

**Purpose:** Set up Tailscale VPN for secure remote access to the GCP VM without
exposing service ports to the public internet.

**Prerequisites:** Module 1 complete. Tailscale account with auth key.

**Requires sudo:** Yes

**Estimated time:** 3-5 minutes

### 10.1 Install Tailscale

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
```

### 10.2 Connect to Tailscale Network

```bash
# Authenticate with your Tailscale auth key
sudo tailscale up --authkey=<YOUR_TAILSCALE_AUTH_KEY>

# Or authenticate interactively
sudo tailscale up
# Follow the URL to authenticate in your browser
```

### 10.3 Update .env with Tailscale Auth Key

```bash
cd ~/project-network-synapse-3

# Set the Tailscale auth key in .env for future reference
sed -i "s/TAILSCALE_AUTH_KEY=tskey-auth-placeholder/TAILSCALE_AUTH_KEY=<YOUR_KEY>/" .env
```

### 10.4 Tighten GCP Firewall (Recommended)

Once Tailscale is working, restrict service ports to Tailscale network only:

```bash
# Get your Tailscale IP
tailscale ip -4
# Example output: 100.x.x.x

# Update firewall to allow only Tailscale CIDR
gcloud compute firewall-rules update synapse-allow-services \
  --source-ranges=100.64.0.0/10
```

### Verification

```bash
# Tailscale is connected
tailscale status
# Expect: shows your machine as connected

# Get Tailscale IP
tailscale ip -4
# Expect: 100.x.x.x address

# Services accessible via Tailscale IP
TSIP=$(tailscale ip -4)
curl -s -o /dev/null -w "%{http_code}" http://$TSIP:8000
# Expect: 200 or 301/302

curl -s -o /dev/null -w "%{http_code}" http://$TSIP:8080
# Expect: 200
```

### Troubleshooting

| Issue                                    | Fix                                                                                                |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `tailscale up` hangs                     | Check firewall allows UDP 41641 (Tailscale WireGuard). Try: `sudo tailscale up --reset`            |
| Auth key expired/invalid                 | Generate new key at https://login.tailscale.com/admin/settings/keys                                |
| Services not accessible via Tailscale IP | Check services bind to `0.0.0.0`, not `127.0.0.1`. Docker Compose default binds to all interfaces. |

---

## End-to-End Verification Checklist

Run this after all modules complete to verify the full platform:

```bash
cd ~/project-network-synapse-3

echo "=== 1. Infrastructure Services ==="
docker compose -f development/docker-compose-deps.yml ps --format "table {{.Name}}\t{{.Status}}"
# Expect: 6 services running

echo ""
echo "=== 2. Infrahub API ==="
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:8000
echo ""
# Expect: HTTP 200 (or 301/302)

echo ""
echo "=== 3. Infrahub Data ==="
curl -s -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "{ DcimDevice { edges { node { hostname { value } } } } }"}' \
  | jq -r '.data.DcimDevice.edges[].node.hostname.value' 2>/dev/null
# Expect: spine01, leaf01, leaf02

echo ""
echo "=== 4. Temporal UI ==="
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:8080
echo ""
# Expect: HTTP 200

echo ""
echo "=== 5. Unit Tests ==="
uv run invoke backend.test-unit 2>&1 | tail -1
# Expect: "41 passed"

echo ""
echo "=== 6. Lint ==="
uv run invoke lint 2>&1 | tail -1
# Expect: "All checks passed!"

echo ""
echo "=== 7. Config Generation ==="
uv run invoke backend.generate-configs --dry-run 2>&1 | head -5
# Expect: Config output for devices

echo ""
echo "=== 8. Containerlab (if deployed) ==="
sudo containerlab inspect --topo containerlab/topology.clab.yml 2>/dev/null \
  | grep -c "running" || echo "Containerlab not deployed (Module 7)"
# Expect: 3 (if deployed)

echo ""
echo "=== DONE ==="
```

---

## Quick Reference: Service URLs

After full deployment, these URLs are available (replace `<IP>` with VM external IP
or Tailscale IP):

| Service       | URL                 | Default Credentials |
| ------------- | ------------------- | ------------------- |
| Infrahub UI   | `http://<IP>:8000`  | admin / infrahub    |
| Temporal UI   | `http://<IP>:8080`  | (no auth)           |
| Neo4j Browser | `http://<IP>:7474`  | neo4j / infrahub    |
| RabbitMQ Mgmt | `http://<IP>:15672` | guest / guest       |
