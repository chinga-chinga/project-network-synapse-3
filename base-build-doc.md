# Manual Installation Guide: Infrahub on GCP with Tailscale

**Project:** Project Network-Synapse  
**Project ID:** `project-network-synapse`  
**Region:** `us-central1-a`  
**Network Security:** Zero Trust (Tailscale Only - No Public Ingress)

---

## Generate Github SSH Keys

#Run these commands on your remote machine (synapse-vm-01):
#Generate a new SSH key:
bash
ssh-keygen
#(Press Enter to accept defaults usually)
#View your public key:
bash
cat ~/.ssh/id_rsa.pub
#Add to GitHub:
#Copy the output starting with ssh-ed25519 ...
#Go to GitHub SSH Settings
#Click New SSH key, give it a Title (e.g., "GCP VM"), and paste the key.
#Clone using SSH:
bash
git clone git@github.com:chinga-chinga/project-network-synapse-3.git

# UV

# Install UV

curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart Shell

exec $SHELL

# Ensure you are in the right UV project

uv sync
source .venv/bin/activate

# External Libraries

## Schema Library

We use the [OpsMill Schema Library](https://github.com/opsmill/schema-library) to provide standard infrastructure schemas (e.g. for servers, circuits). This is included as a git submodule.

To add the library (reference):

```bash
git submodule add https://github.com/opsmill/schema-library.git library/schema-library
```

To initialize or update the library (downloads files to `library/schema-library`):

```bash
git submodule update --init --recursive
```

## Monitoring resources

free -h

## Phase 1: Infrastructure Provisioning

_Run these commands in your local terminal._

### 1. Set Project Context

Ensure your Google Cloud CLI is targeting the correct project.

```bash
gcloud config set project project-network-synapse
```

### 2. Optimize Network for Tailscale

Create a firewall rule to allow UDP traffic on port 41641. This ensures a Direct (low latency) connection instead of a Relayed connection.

```bash
gcloud compute firewall-rules create allow-tailscale-direct \
    --description="Allow Tailscale UDP for direct mesh connectivity" \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=udp:41641 \
    --source-ranges=0.0.0.0/0
```

### 3. Create Virtual Machine

Provision an `e2-standard-2` (2 vCPU, 8 GB RAM) to satisfy Infrahub's Neo4j memory requirements.

```bash
gcloud compute instances create infrahub-synapse \
    --zone=us-central1-a \
    --machine-type=e2-standard-2 \
    --image-family=debian-12 \
    --image-project=debian-cloud \
    --boot-disk-size=40GB \
    --boot-disk-type=pd-balanced \
    --tags=tailscale-node
```

## Phase 2: Software Installation

_Run these commands inside the VM._

### 1. SSH into the VM

```bash
gcloud compute ssh infrahub-synapse --zone=us-central1-a
```

### 2. Install Docker

```bash
# Update system packages
sudo apt-get update && sudo apt-get install -y curl git

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group
sudo usermod -aG docker $USER
# (Optional) Log out and back in for group changes to take effect, or use sudo below
```

### 3. Install & Authenticate Tailscale

# Install Tailscale

curl -fsSL https://tailscale.com/install.sh | sh

# Authenticate

# Load environment variables (locally) or set them in your CI/CD

export TAILSCALE_AUTH_KEY=<YOUR_KEY>

sudo tailscale up --authkey=$TAILSCALE_AUTH_KEY --hostname=synapse-vm-01

# Tailscale check

tailscale status
tailscale ip -4

**Direct**: Firewall rule from Phase 1 is working.
**Relay**: Firewall rule is missing or blocked.

# Check for port conflicts

sudo ss -tulpn | grep LISTEN

**The "Tailscale Ping" Test**

# This is the most definitive test. Unlike a standard system ping, tailscale ping shows exactly how the packet is traveling. To test, toggle the tailscale enable on your local client. Run this from your local computer (the one you are using to access the VM):

```bash
tailscale ping <VM-TAILSCALE-IP>
```

### 4. Deploy Infrahub (Light Stack)

# Create directory and download (no sudo usually needed for curl/mkdir in home dir)

mkdir -p ~/infrahub && cd ~/infrahub
curl -L https://infrahub.opsmill.io -o docker-compose.yml

** Best Practice: Add your user to the docker group
** To avoid typing sudo every time (and to prevent potential permission issues with files created by the containers), it is standard practice on Ubuntu to add your user to the docker group.

# Run these commands once:

````bash
# Create the group if it doesn't exist
sudo groupadd docker

# Add your current user to the group
sudo usermod -aG docker $USER

# Apply the group changes to your current session
newgrp docker

**Launch Stack**
# Start the stack (sudo is required to talk to the Docker daemon). Run this from the directory where you downloaded the docker-compose.yml:
# -p sets the project name
# -d runs it in the background (detached mode)
sudo docker compose -p infrahub up -d

**Monitor the Startup (Wait for "Healthy")**
# This will show you the logs as they come in, and you can see when each service is ready
sudo docker compose logs -f

*** Troubleshooting & LogsIf it feels like it's taking too long, or a container says unhealthy, check the logs to see what's happening***

#View all logs

```bash
sudo docker compose -p infrahub logs -f

#Check only the API
```bash
sudo docker compose -p infrahub logs -f infrahub
#Check the Database

sudo docker compose -p infrahub logs -f database

#TEST CONNECTIVITY IN BROWSER
http://synapse-vm-01:8000/

### 4. Deploy Temporal

# Create a dedicated directory
mkdir -p ~/temporal && cd ~/temporal

# Clone the official repository
git clone https://github.com/temporalio/docker-compose.git .

# List the files to see different database options (MySQL, Cassandra, etc.)
ls -l

# Start Temporal
docker compose -p temporal up -d

# Check Status:
sudo docker compose ps

Temporal Web UI:
http://<YOUR_VM_TAILSCALE_IP>:8080

# gRPC Port (for your code/SDKs):
<YOUR_VM_TAILSCALE_IP>:7233

** Install Temporal CLI **
# To interact with your new cluster from the command line (to register namespaces or check workflow status), install the Temporal CLI:
# Download and install for Linux
curl -sSf https://temporal.download/cli.sh | sh

# Add it to your path (or restart your terminal)
export PATH="$PATH:$HOME/.temporalio/bin"

# Test the connection to your server
temporal env set local.address <YOUR_VM_TAILSCALE_IP>:7233 #(NOT done this one yet)
temporal operator cluster health

** INstall Contanerlab **
# Download and install the latest release
# This script auto-detects your OS and installs the latest binary
bash -c "$(curl -sL https://get.containerlab.dev)"

# permissions setu. Add yourself to the group
sudo usermod -aG clab_admins $USER

# Refresh your group membership in the current session
newgrp clab_admins

# Verify Installation
clab version

# Accessing Lab Nodes via Tailscale
# When you deploy a lab, Containerlab assigns internal IP addresses (usually 172.20.20.x) to the network nodes (like Arista or Nokia switches).
# Direct Access: You can access these nodes from inside the VM using docker exec or ssh.
# Tailscale Access: If you want to access these virtual switches from your laptop via Tailscale, you have two options:
# Tailscale Subnet Router: Run sudo tailscale up --advertise-routes=172.20.20.0/24. This allows your laptop to "see" the internal container network.
# SSH via VM: Use your VM as a jump host.

# Generate Configuration File (.env)
# This dynamically fetches your Tailscale IP to ensure the UI works correctly

# Nested Virtualization (Crucial for GCP)
# Some advanced network images (like Cisco vRouter or Juniper vMX) require Nested Virtualization to be enabled on your GCP VM instance.
# Most container-native images (Nokia SR Linux, Arista cEOS, FRR) will work fine without it.
# If you plan to run heavy VM-based nodes, you must ensure your GCP VM was created with --enable-nested-virtualization.

# Managing the LabCommandAction
#See running nodes and their IPs.
sudo clab inspect -t <file>.yml
#Stop and remove the lab.
sudo clab destroy -t <file>.yml
#Generate a visual topology (viewable via a web browser).
sudo clab graph -t <file>.yml


TS_IP=$(tailscale ip -4)

cat <<EOF > .env
INFRAHUB_ADDRESS=0.0.0.0
INFRAHUB_PORT=8000
INFRAHUB_UI_PUBLIC_URL=http://${TS_IP}:8000
EOF

# Start Services
docker compose up -d
````

## Phase 3: Verification

### 1. Check Service Health

Ensure all 4 containers (`api`, `web`, `neo4j`, `redis`) are running:

```bash
docker ps
```

### 2. Verify Tailscale Performance

Check if the connection is `Direct` (optimized) or `Relay` (slow):

```bash
tailscale status
```

- **Direct**: Firewall rule from Phase 1 is working.
- **Relay**: Firewall rule is missing or blocked.

### 3. Access Application

Open your browser (from a device on the same Tailscale network) and navigate to:

> `http://<Tailscale-IP>:8000`

**Default Credentials:** `admin` / `admin`
