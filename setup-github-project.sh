#!/usr/bin/env bash
# setup-github-project.sh — Create GitHub labels, milestones, and issues for the 4-week POC/MVP
# Run from repo root: bash setup-github-project.sh
set -euo pipefail

REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
echo "=== Setting up project tracking for: $REPO ==="
echo ""

LABEL_COUNT=0
MILESTONE_COUNT=0
ISSUE_COUNT=0

# ─────────────────────────────────────────────
# Step 1: Labels
# ─────────────────────────────────────────────
echo "── Creating Labels ──"

create_label() {
  local name="$1" color="$2" desc="$3"
  gh label create "$name" --color "$color" --description "$desc" --force
  LABEL_COUNT=$((LABEL_COUNT + 1))
}

create_label "ci-cd"          "1D76DB" "CI/CD pipeline"
create_label "infrahub"       "0E8A16" "Infrahub source of truth"
create_label "temporal"       "5319E7" "Temporal workflows"
create_label "containerlab"   "D93F0B" "Containerlab topology"
create_label "testing"        "FBCA04" "Tests and coverage"
create_label "observability"  "006B75" "Monitoring and logging"
create_label "documentation"  "C5DEF5" "Docs and runbooks"
create_label "security"       "B60205" "Security and secrets"
create_label "srlinux"        "FF6600" "Nokia SR Linux"
create_label "ansible"        "EE0000" "Ansible playbooks"

echo "  ✓ $LABEL_COUNT labels created"
echo ""

# ─────────────────────────────────────────────
# Step 2: Milestones
# ─────────────────────────────────────────────
echo "── Creating Milestones ──"

TODAY=$(date -u +%Y-%m-%d)
if [[ "$(uname)" == "Darwin" ]]; then
  DUE_W1=$(date -u -v+7d +%Y-%m-%dT23:59:59Z)
  DUE_W2=$(date -u -v+14d +%Y-%m-%dT23:59:59Z)
  DUE_W3=$(date -u -v+21d +%Y-%m-%dT23:59:59Z)
  DUE_W4=$(date -u -v+28d +%Y-%m-%dT23:59:59Z)
else
  DUE_W1=$(date -u -d "+7 days" +%Y-%m-%dT23:59:59Z)
  DUE_W2=$(date -u -d "+14 days" +%Y-%m-%dT23:59:59Z)
  DUE_W3=$(date -u -d "+21 days" +%Y-%m-%dT23:59:59Z)
  DUE_W4=$(date -u -d "+28 days" +%Y-%m-%dT23:59:59Z)
fi

create_milestone() {
  local title="$1" desc="$2" due="$3"
  # Check if milestone already exists
  existing=$(gh api "repos/${REPO}/milestones" --jq ".[] | select(.title==\"${title}\") | .number" 2>/dev/null || true)
  if [ -n "$existing" ]; then
    echo "  ⏭ Milestone '$title' already exists (#$existing)"
  else
    gh api "repos/${REPO}/milestones" \
      -f title="$title" \
      -f description="$desc" \
      -f due_on="$due" \
      -f state="open" --silent
    echo "  ✓ Created milestone: $title (due $due)"
  fi
  MILESTONE_COUNT=$((MILESTONE_COUNT + 1))
}

create_milestone "Week 1: Foundation + CI/CD Skeleton" \
  "Infrastructure, repo structure, CI pipeline, Infrahub schemas, initial tests" \
  "$DUE_W1"

create_milestone "Week 2: Configuration + Observability" \
  "Config generation from Infrahub, template tests, Prometheus, Grafana, ELK" \
  "$DUE_W2"

create_milestone "Week 3: Deployment + Validation" \
  "Ansible playbooks, device deployment, integration tests, post-deployment checks" \
  "$DUE_W3"

create_milestone "Week 4: Polish + Demo Prep" \
  "Complete observability, CI/CD to staging, documentation, demo script" \
  "$DUE_W4"

echo "  ✓ $MILESTONE_COUNT milestones created"
echo ""

# ─────────────────────────────────────────────
# Step 3: Issues
# ─────────────────────────────────────────────
echo "── Creating Issues ──"

create_issue() {
  local title="$1" body="$2" labels="$3" milestone="$4"
  gh issue create \
    --title "$title" \
    --body "$body" \
    --label "$labels" \
    --milestone "$milestone"
  ISSUE_COUNT=$((ISSUE_COUNT + 1))
  echo "  ✓ #$ISSUE_COUNT: $title"
}

# ── Week 1: Foundation + CI/CD Skeleton (8 issues) ──
echo ""
echo "  Week 1 issues..."

create_issue \
  "Set up PR validation workflow (.github/workflows/pr-validation.yml)" \
  "$(cat <<'BODY'
Create GitHub Actions PR validation pipeline with:
- Black formatting check
- isort import sorting
- Pylint linting (continue-on-error initially)
- MyPy type checking (continue-on-error initially)
- Bandit security scan with SARIF upload
- Gitleaks secrets detection
- Unit tests with pytest + coverage (80% target)
- PR summary job that checks all results
- Triggers on PRs to main and develop branches
BODY
)" \
  "ci-cd" \
  "Week 1: Foundation + CI/CD Skeleton"

create_issue \
  "Set up push-to-develop CI workflow (.github/workflows/ci.yml)" \
  "$(cat <<'BODY'
Create CI workflow triggered on push to develop. Same jobs as PR validation plus integration test placeholder job (skipped for now, implemented Week 3).
BODY
)" \
  "ci-cd" \
  "Week 1: Foundation + CI/CD Skeleton"

create_issue \
  "Create project config files (pyproject.toml, pylintrc, mypy.ini, pytest.ini)" \
  "$(cat <<'BODY'
Set up Python tooling configuration:
- pyproject.toml: Black (line-length=100, py311), isort (profile=black), bandit (exclude tests)
- .pylintrc: max-line-length=100, disable missing docstrings for now
- mypy.ini: Python 3.11, ignore_missing_imports=True
- pytest.ini: markers for unit/integration/slow/pre_deployment/post_deployment
- requirements.txt: infrahub-sdk, temporalio, nornir, scrapli, pygnmi, grpcio, jinja2, pydantic, httpx, pyyaml
- requirements-dev.txt: pytest, pytest-cov, pytest-asyncio, black, isort, pylint, mypy, bandit, detect-secrets, pre-commit
BODY
)" \
  "ci-cd" \
  "Week 1: Foundation + CI/CD Skeleton"

create_issue \
  "Create test scaffolding (conftest.py, placeholder tests)" \
  "$(cat <<'BODY'
Set up test directory structure:
- tests/conftest.py with Nokia SR Linux fixtures:
  - sample_device_data: spine01, nokia_srlinux platform, AS 65000
  - sample_bgp_session: with network_instance and group fields
  - spine_leaf_topology: all 3 devices with ASNs and mgmt IPs
- tests/unit/test_placeholder.py: import tests (jinja2, yaml, pygnmi, grpc), fixture validation
- tests/integration/test_placeholder.py: skipped tests for Infrahub, Containerlab gNMI, JSON-RPC
- All __init__.py files in place
BODY
)" \
  "testing,srlinux" \
  "Week 1: Foundation + CI/CD Skeleton"

create_issue \
  "Load Infrahub schemas into version control" \
  "$(cat <<'BODY'
Version-control Infrahub schema definitions in infrahub/schemas/:
- NetworkDevice schema (hostname, device_type, management_ip, ASN, role, status)
- NetworkInterface schema (name, type, enabled, IP addresses)
- BGPSession schema (local/remote ASN, local/remote IP, network_instance, group)
- RoutingInstance schema
- Create scripts/infrahub_schema_loader.py to load and validate schemas
- Verify schemas load correctly against running Infrahub instance
BODY
)" \
  "infrahub" \
  "Week 1: Foundation + CI/CD Skeleton"

create_issue \
  "Containerlab SR Linux topology file" \
  "$(cat <<'BODY'
Create containerlab/topology.clab.yml defining:
- spine01: Nokia SR Linux ixrd3, AS 65000, mgmt 172.20.20.10
- leaf01: Nokia SR Linux ixrd2, AS 65001, mgmt 172.20.20.11
- leaf02: Nokia SR Linux ixrd2, AS 65002, mgmt 172.20.20.12
- Image: ghcr.io/nokia/srlinux:latest
- Spine-leaf links between spine01↔leaf01 and spine01↔leaf02
- Management network definition
BODY
)" \
  "containerlab,srlinux" \
  "Week 1: Foundation + CI/CD Skeleton"

create_issue \
  "Write unit tests for Infrahub GraphQL queries" \
  "$(cat <<'BODY'
Unit tests with mocked Infrahub SDK:
- Query device by hostname
- Query device by role (spine/leaf)
- Query all devices
- Query interfaces by device
- Query BGP sessions
- Handle empty results
- Handle connection errors
- Target: 10+ unit tests following AAA pattern
BODY
)" \
  "testing,infrahub" \
  "Week 1: Foundation + CI/CD Skeleton"

create_issue \
  "Configure branch protection rules" \
  "$(cat <<'BODY'
After first successful CI run, configure in GitHub repo Settings → Branches:
- Protection rule on main: require status checks, require PR, select CI job names
- Protection rule on develop: require status checks, require PR
- Optional: require 1 reviewer for main
BODY
)" \
  "ci-cd" \
  "Week 1: Foundation + CI/CD Skeleton"

# ── Week 2: Configuration + Observability (6 issues) ──
echo ""
echo "  Week 2 issues..."

create_issue \
  "Config generation from Infrahub (query + render)" \
  "$(cat <<'BODY'
Build config generation pipeline:
- Script to query Infrahub GraphQL API for device intended state
- Produce SR Linux JSON configs (not CLI commands)
- Decide on approach: Infrahub built-in transformation engine vs standalone rendering
- Output per-device JSON config files matching SR Linux YANG model paths
- Handle BGP, interfaces, and routing instance configs
BODY
)" \
  "infrahub,srlinux" \
  "Week 2: Configuration + Observability"

create_issue \
  "Unit tests for config generation" \
  "$(cat <<'BODY'
Test config generation pipeline:
- Valid device data → correct SR Linux JSON output
- Missing required data → appropriate error
- BGP config renders with correct YANG paths
- Interface config renders correctly
- Multi-device generation works
- Target: 10+ tests, integrated into CI pipeline
BODY
)" \
  "testing,srlinux" \
  "Week 2: Configuration + Observability"

create_issue \
  "CI pipeline runs all tests on PR" \
  "$(cat <<'BODY'
Verify end-to-end CI:
- PR triggers pr-validation workflow
- All code quality checks pass (or continue-on-error where configured)
- Unit tests pass with >80% coverage
- Security scan runs without critical findings
- Gitleaks secrets detection passes
- Fix any remaining CI failures from Week 1 setup
BODY
)" \
  "ci-cd,testing" \
  "Week 2: Configuration + Observability"

create_issue \
  "Deploy Prometheus + Node Exporter" \
  "$(cat <<'BODY'
Set up metrics collection on GCP VM:
- Prometheus 2.45+ deployed
- Node Exporter for system metrics (CPU, memory, disk, network)
- Scrape config targeting all services (Infrahub, Temporal, Node Exporter)
- 15-day retention configured
- Verify metrics are being collected and queryable
BODY
)" \
  "observability" \
  "Week 2: Configuration + Observability"

create_issue \
  "Deploy Grafana with System Health dashboard" \
  "$(cat <<'BODY'
Set up visualization:
- Grafana 10+ deployed, connected to Prometheus datasource
- System Health dashboard: CPU usage, memory usage, disk usage
- 30-second auto-refresh
- Verify data is flowing from Prometheus to Grafana panels
BODY
)" \
  "observability" \
  "Week 2: Configuration + Observability"

create_issue \
  "Deploy ELK stack for centralized logging" \
  "$(cat <<'BODY'
Set up log aggregation:
- Elasticsearch 8.x for log storage
- Logstash for log ingestion and transformation
- Kibana for log exploration
- Filebeat shipping logs from application hosts
- 30-day retention with index lifecycle management
- Verify logs are searchable in Kibana
BODY
)" \
  "observability" \
  "Week 2: Configuration + Observability"

# ── Week 3: Deployment + Validation (7 issues) ──
echo ""
echo "  Week 3 issues..."

create_issue \
  "Ansible playbook for SR Linux config deployment" \
  "$(cat <<'BODY'
Create ansible/playbooks/deploy_bgp.yml:
- Deploy generated JSON configs to SR Linux devices
- Use gNMI or JSON-RPC for config push (NOT SSH/CLI)
- Pre-deployment config backup
- Post-deployment connectivity validation
- Rollback support on failure
- Inventory sourced from Infrahub (or static for now)
BODY
)" \
  "ansible,srlinux" \
  "Week 3: Deployment + Validation"

create_issue \
  "Deploy configs to Containerlab SR Linux devices" \
  "$(cat <<'BODY'
End-to-end manual config deployment:
- Generate configs from Infrahub data
- Push to spine01, leaf01, leaf02 via gNMI
- Verify BGP sessions establish between spine and leaves
- Validate routing tables have expected prefixes
- Document the manual process before Temporal automation
BODY
)" \
  "containerlab,srlinux" \
  "Week 3: Deployment + Validation"

create_issue \
  "Set up Suzieq for network state collection" \
  "$(cat <<'BODY'
Deploy Suzieq network observability:
- Configure inventory with SR Linux devices (172.20.20.10-12)
- 5-minute polling interval
- Collect: device facts, interfaces, BGP, routes, LLDP, MAC, ARP
- Validate data collection working
- Will feed drift detection later
BODY
)" \
  "observability,srlinux" \
  "Week 3: Deployment + Validation"

create_issue \
  "Integration tests (Infrahub + Containerlab)" \
  "$(cat <<'BODY'
Implement real integration tests:
- Infrahub connectivity and CRUD operations
- SR Linux gNMI connectivity (pygnmi)
- SR Linux JSON-RPC connectivity
- Full config generation flow against live Infrahub
- Config deployment to Containerlab devices
- State validation post-deployment
- Target: 15+ integration tests
BODY
)" \
  "testing,infrahub,containerlab" \
  "Week 3: Deployment + Validation"

create_issue \
  "Post-deployment validation checks" \
  "$(cat <<'BODY'
Validation framework:
- BGP session state verification (all sessions established)
- Interface status checks (oper-state up)
- Route table validation (expected prefixes present)
- LLDP neighbor verification (correct adjacencies)
- Connectivity tests between spine and leaf devices
- Report results in structured format
BODY
)" \
  "testing,srlinux" \
  "Week 3: Deployment + Validation"

create_issue \
  "Configuration hygiene checker" \
  "$(cat <<'BODY'
Build config compliance validation:
- Check for required config elements (NTP, logging, AAA)
- Detect dangerous or missing configuration
- Verify SR Linux best practices followed
- Report compliance status (could feed back to Infrahub)
- Run as pre-deployment gate in CI pipeline
BODY
)" \
  "testing,security" \
  "Week 3: Deployment + Validation"

create_issue \
  "Prometheus alert rules" \
  "$(cat <<'BODY'
Configure Alertmanager rules:
- BGP session down (critical)
- Interface flap detection (warning)
- High CPU/memory on GCP VM (warning)
- Infrahub unreachable (critical)
- Temporal worker unhealthy (critical)
- Route to Slack channel
BODY
)" \
  "observability" \
  "Week 3: Deployment + Validation"

# ── Week 4: Polish + Demo Prep (8 issues) ──
echo ""
echo "  Week 4 issues..."

create_issue \
  "Complete all 5 Grafana dashboards" \
  "$(cat <<'BODY'
Build remaining dashboards beyond System Health:
1. System Health (done Week 2)
2. Network Operations: BGP session status, interface stats, route counts
3. Automation Pipeline: Temporal workflow success/failure rates, duration
4. Compliance Tracking: drift scores, hygiene check results
5. Capacity Planning: resource utilization trends, growth projections
BODY
)" \
  "observability" \
  "Week 4: Polish + Demo Prep"

create_issue \
  "Slack alert integration" \
  "$(cat <<'BODY'
Configure Alertmanager → Slack:
- Critical alerts: immediate notification with @channel
- Warning alerts: batched every 15 minutes
- Info alerts: daily digest
- Include runbook links in alert messages
- Test alert routing end-to-end
BODY
)" \
  "observability" \
  "Week 4: Polish + Demo Prep"

create_issue \
  "Log aggregation working end-to-end" \
  "$(cat <<'BODY'
Verify full logging pipeline:
- Python apps → structured JSON logs → Filebeat → Logstash → Elasticsearch → Kibana
- Temporal workflow logs captured
- Infrahub API logs captured
- Log correlation across services (trace IDs if possible)
- Search and filter working in Kibana dashboards
BODY
)" \
  "observability" \
  "Week 4: Polish + Demo Prep"

create_issue \
  "CI/CD deploy workflow to staging" \
  "$(cat <<'BODY'
Create .github/workflows/deploy.yml:
- Manual trigger via workflow_dispatch
- Environment selection dropdown (dev/staging/prod)
- Version input (tag or branch)
- Pre-deployment validation checks
- Auto-deploy to staging on merge to main
- Manual approval gate for production
- Rollback capability
BODY
)" \
  "ci-cd" \
  "Week 4: Polish + Demo Prep"

create_issue \
  "Architecture documentation" \
  "$(cat <<'BODY'
Create comprehensive project docs:
- README.md: project overview, quickstart, prereqs
- Architecture diagram (7-layer model)
- Component interaction documentation
- Infrahub GraphQL API reference / query examples
- SR Linux JSON config format reference
- Containerlab topology documentation
BODY
)" \
  "documentation" \
  "Week 4: Polish + Demo Prep"

create_issue \
  "Create demo script" \
  "$(cat <<'BODY'
Step-by-step demo script (target: under 10 minutes):
1. Show Infrahub UI — add new BGP peer
2. Show CI pipeline triggered by change
3. Show SR Linux JSON config generated
4. Show deployment to Containerlab devices via gNMI
5. Show post-deployment validation passing
6. Show Grafana dashboards updating in real-time
7. Show drift detection and remediation flow
BODY
)" \
  "documentation" \
  "Week 4: Polish + Demo Prep"

create_issue \
  "Operational runbooks" \
  "$(cat <<'BODY'
Create runbooks for:
- Adding a new device to automation platform
- Troubleshooting failed Temporal workflows
- Handling drift detection alerts
- Emergency rollback procedure
- Infrahub / Temporal disaster recovery
- Break-glass manual SSH access to devices
BODY
)" \
  "documentation" \
  "Week 4: Polish + Demo Prep"

create_issue \
  "End-to-end test suite" \
  "$(cat <<'BODY'
Full E2E tests covering the complete workflow:
- Add BGP peer in Infrahub → config generated → deployed to SR Linux → validated
- Temporal workflow orchestrates full change lifecycle
- Drift detection finds intentional change and remediates
- Rollback on deployment failure works correctly
- Target: 5+ E2E tests
BODY
)" \
  "testing" \
  "Week 4: Polish + Demo Prep"

# ─────────────────────────────────────────────
# Step 4: Summary
# ─────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════"
echo "  GitHub Project Setup Complete"
echo "═══════════════════════════════════════════"
echo "  Labels created:     $LABEL_COUNT"
echo "  Milestones created: $MILESTONE_COUNT"
echo "  Issues created:     $ISSUE_COUNT"
echo ""
echo "  Next steps:"
echo "  1. Create a GitHub Project board at:"
echo "     https://github.com/$REPO/projects"
echo "  2. Add all issues to the project board"
echo "  3. Close issues 1-4 (already completed in Week 1)"
echo "═══════════════════════════════════════════"
