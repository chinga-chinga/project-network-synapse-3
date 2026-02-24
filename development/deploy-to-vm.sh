#!/usr/bin/env bash
# deploy-to-vm.sh — Automated deployment script for the GCP VM
# Called by GitHub Actions CD pipeline or manually
set -euo pipefail

REMOTE_USER="${REMOTE_USER:-anton}"
REMOTE_HOST="${REMOTE_HOST:?VM_HOST not set}"
REMOTE_DIR="/home/${REMOTE_USER}/project-network-synapse-3"
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=10"

echo "══════════════════════════════════════"
echo "  Deploying to: ${REMOTE_HOST}"
echo "  Branch:       ${GITHUB_REF_NAME:-$(git rev-parse --abbrev-ref HEAD)}"
echo "  Commit:       ${GITHUB_SHA:-$(git rev-parse --short HEAD)}"
echo "══════════════════════════════════════"

# Step 1: Pull latest code
echo "→ Pulling latest code..."
ssh ${SSH_OPTS} "${REMOTE_USER}@${REMOTE_HOST}" "
  export PATH=\$HOME/.local/bin:\$PATH
  cd ${REMOTE_DIR}
  git fetch origin
  git reset --hard origin/main
  git submodule update --init --recursive
"

# Step 2: Install/update dependencies
echo "→ Installing dependencies..."
ssh ${SSH_OPTS} "${REMOTE_USER}@${REMOTE_HOST}" "
  export PATH=\$HOME/.local/bin:\$PATH
  cd ${REMOTE_DIR}
  uv sync --all-groups
"

# Step 3: Restart the worker
echo "→ Restarting synapse-worker service..."
ssh ${SSH_OPTS} "${REMOTE_USER}@${REMOTE_HOST}" "
  sudo systemctl restart synapse-worker
  sleep 3
  sudo systemctl is-active synapse-worker
"

# Step 4: Health check
echo "→ Running health checks..."
ssh ${SSH_OPTS} "${REMOTE_USER}@${REMOTE_HOST}" "
  export PATH=\$HOME/.local/bin:\$PATH
  cd ${REMOTE_DIR}

  # Check worker is alive
  pgrep -f 'synapse_workers.worker' > /dev/null && echo '  ✓ Worker process running' || echo '  ✗ Worker not running'

  # Check Temporal connectivity
  curl -s -o /dev/null -w '  Temporal UI: HTTP %{http_code}\n' http://localhost:8080

  # Check Infrahub connectivity
  curl -s -o /dev/null -w '  Infrahub:    HTTP %{http_code}\n' http://localhost:8000
"

echo "══════════════════════════════════════"
echo "  Deployment complete!"
echo "══════════════════════════════════════"
