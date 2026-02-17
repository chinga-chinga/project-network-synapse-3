# Network Synapse

Network automation platform for managing Nokia SR Linux datacenter fabric switches using Infrahub as Source of Truth, Temporal for workflow orchestration, and Containerlab for virtual network labs.

## Architecture

```
  Infrahub (SoT)          Temporal            Nokia SR Linux
  ┌────────────┐     ┌──────────────┐     ┌──────────────────┐
  │ GraphQL API│────>│  Workflows   │────>│ spine01 (IXR-D3) │
  │ Schemas    │     │  Activities  │     │ leaf01  (IXR-D2) │
  │ Inventory  │     │  Workers     │     │ leaf02  (IXR-D2) │
  └────────────┘     └──────────────┘     └──────────────────┘
       │                    │                      │
       └──── Query SoT ────┘──── gNMI Deploy ─────┘
```

**Pipeline:** Query Infrahub SoT -> Render Jinja2 templates -> Deploy via gNMI -> Validate state

## Quick Start

```bash
# Prerequisites: Python 3.11+, uv (https://docs.astral.sh/uv/)

# Clone and setup
git clone https://github.com/chinga-chinga/project-network-synapse-3.git
cd project-network-synapse-3
git submodule update --init --recursive
uv sync --all-groups

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run invoke backend.test-unit
```

## Project Structure

```
backend/                 # Python package: network-synapse
  network_synapse/       #   Infrahub SoT, config generation, schema management
workers/                 # Python package: network-synapse-workers
  synapse_workers/       #   Temporal workflows, activities, worker
tests/                   # Unit + integration tests
containerlab/            # Nokia SR Linux spine-leaf lab topology
ansible/                 # Ansible playbooks
development/             # Docker Compose + Dockerfile for dev environment
docs/                    # Project documentation
dev/                     # Developer docs (Context Nuggets pattern)
tasks/                   # Invoke task runner modules
changelog/               # Towncrier changelog fragments
library/                 # Git submodule: opsmill/schema-library
```

## Key Commands

```bash
uv run invoke format              # Format code (ruff)
uv run invoke lint                # Lint code (ruff)
uv run invoke scan                # Security scan (bandit)
uv run invoke backend.test-unit   # Unit tests
uv run invoke backend.test-all    # All tests with coverage
uv run invoke backend.load-schemas  # Load schemas into Infrahub
uv run invoke backend.seed-data   # Seed data into Infrahub
uv run invoke workers.start       # Start Temporal worker
uv run invoke dev.deps            # Start infrastructure dependencies
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Source of Truth | [Infrahub](https://github.com/opsmill/infrahub) (OpsMill) |
| Workflow Engine | [Temporal](https://temporal.io/) |
| Network Lab | [Containerlab](https://containerlab.dev/) + Nokia SR Linux |
| Package Manager | [uv](https://docs.astral.sh/uv/) |
| Linter/Formatter | [Ruff](https://docs.astral.sh/ruff/) |
| CI/CD | GitHub Actions |
| Device Communication | gNMI (pygnmi) |
| Config Templates | Jinja2 |

## Lab Topology

3-node Nokia SR Linux spine-leaf fabric on GCP:

- **spine01** (IXR-D3, AS65000) — 4 fabric links
- **leaf01** (IXR-D2, AS65001) — 2 uplinks
- **leaf02** (IXR-D2, AS65002) — 2 uplinks
- Management: `172.20.20.0/24`
- Underlay: eBGP on `/31` point-to-point links

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions and development workflow.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
