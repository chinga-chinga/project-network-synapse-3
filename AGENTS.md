# Network Synapse — Agent Knowledge Map

> This file is the entry point for AI coding agents working on this project.
> It provides a comprehensive map of the codebase, conventions, and development workflow.

## What Is This Project?

**Network Synapse** is a network automation platform for managing Nokia SR Linux datacenter fabric switches. It automates the full lifecycle of network configuration changes against a spine-leaf lab topology using:

- **Infrahub** (OpsMill) — Graph-based Source of Truth (SoT) for network inventory, schemas, and intended state
- **Temporal** — Durable workflow orchestration engine for auditable automation workflows
- **Containerlab** — Nokia SR Linux virtual network labs on GCP

**Pipeline:** Query Infrahub SoT -> Render Jinja2 config templates -> Deploy via gNMI to SR Linux -> Validate post-deploy state

## Repository Structure

```
project-network-synapse-3/
├── backend/                    # Python package: network-synapse
│   ├── pyproject.toml
│   └── network_synapse/
│       ├── data/               # Infrahub SoT data seeding (populate_sot.py, seed_data.yml)
│       ├── schemas/            # Infrahub schema extensions (load_schemas.py, *.yml)
│       ├── scripts/            # Automation scripts (generate/deploy/validate configs)
│       └── templates/          # Jinja2 templates for Nokia SR Linux (gNMI-ready JSON)
│
├── workers/                    # Python package: network-synapse-workers
│   ├── pyproject.toml
│   └── synapse_workers/
│       ├── worker.py           # Temporal worker entry point
│       ├── activities/         # Temporal activity definitions
│       └── workflows/          # Temporal workflow definitions
│
├── tests/                      # Test suite (unit + integration)
│   ├── conftest.py             # Shared fixtures (spine-leaf topology, BGP sessions)
│   ├── unit/
│   └── integration/
│
├── ansible/                    # Ansible playbooks and inventory
├── containerlab/               # Containerlab topology definition (spine-leaf lab)
├── development/                # Docker Compose, Dockerfile for dev environment
├── docs/                       # Project documentation (markdown)
├── library/                    # Git submodule: opsmill/schema-library
├── tasks/                      # Invoke task runner modules
├── changelog/                  # Towncrier changelog fragments
│
├── dev/                        # Developer documentation (Context Nuggets)
│   ├── adr/                    # Architecture Decision Records
│   ├── commands/               # Reusable AI agent commands
│   ├── guidelines/             # Coding standards and conventions
│   ├── guides/                 # Step-by-step procedures
│   ├── knowledge/              # Architecture explanations
│   ├── prompts/                # Prompt templates
│   └── skills/                 # AI agent skills
│
├── pyproject.toml              # Root workspace config (uv + all tool configs)
├── .pre-commit-config.yaml     # Pre-commit hooks (ruff, detect-secrets, gitleaks)
└── .github/                    # CI/CD workflows, PR/issue templates, CODEOWNERS
```

## Workspace Architecture

This is a **uv workspace monorepo** with two packages:

| Package | Import Path | Description |
|---------|-------------|-------------|
| `network-synapse` | `network_synapse` | Backend: Infrahub interaction, config generation, schema management |
| `network-synapse-workers` | `synapse_workers` | Temporal workers: durable workflows, activities |

Workers depend on the backend package. Both are linked via `[tool.uv.sources]` in the root `pyproject.toml`.

## Key Commands

```bash
# Setup
uv sync --all-groups                    # Install all dependencies

# Development
uv run invoke format                    # Format code (ruff)
uv run invoke lint                      # Lint code (ruff)
uv run invoke scan                      # Security scan (bandit + detect-secrets)
uv run invoke check-all                 # All quality checks

# Testing
uv run invoke backend.test-unit         # Unit tests
uv run invoke backend.test-integration  # Integration tests
uv run invoke backend.test-all          # All tests

# Backend operations
uv run invoke backend.load-schemas      # Load schemas into Infrahub
uv run invoke backend.seed-data         # Seed data into Infrahub
uv run invoke backend.typecheck         # MyPy type checking

# Workers
uv run invoke workers.start             # Start Temporal worker

# Infrastructure
uv run invoke dev.deps                  # Start infrastructure dependencies
uv run invoke dev.deps-stop             # Stop infrastructure dependencies
uv run invoke dev.build                 # Build Docker images
uv run invoke dev.lab-deploy            # Deploy Containerlab topology
uv run invoke dev.lab-destroy           # Destroy Containerlab topology

# Documentation
uv run invoke docs.lint-yaml            # Lint YAML files
```

## Coding Standards

- **Formatter/Linter:** Ruff (replaces black, isort, pylint, flake8)
- **Line length:** 120 characters
- **Python version:** 3.11+
- **Type hints:** Required on all public functions; `ignore_missing_imports = true` in mypy
- **Import order:** stdlib -> third-party -> first-party (`network_synapse`, `synapse_workers`)
- **Docstrings:** Required on all modules, classes, and public functions
- **Quote style:** Double quotes
- **Line endings:** LF (Unix)

See `dev/guidelines/python.md` for full details.

## Git Workflow

- **`main`** — Protected, production-ready code. No direct commits.
- **`develop`** — Integration branch. PRs merge here first.
- **Feature branches:** `feature/<description>` from `develop`
- **Bug fixes:** `fix/<description>` from `develop`
- **Infrastructure:** `dev/<description>` from `develop`
- **Commit style:** Conventional Commits (`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`)

See `dev/guidelines/git-workflow.md` for full details.

## Changelog

Uses Towncrier for changelog management. When making changes, add a fragment file:

```bash
# Format: changelog/<issue-number>.<type>.md
# Types: added, changed, deprecated, removed, fixed, security
echo "Added BGP session validation workflow" > changelog/42.added.md
```

See `dev/guidelines/changelog.md` for details.

## Developer Documentation (dev/)

This project follows the **Context Nuggets** pattern (ADR-0001) for developer documentation:

| Directory | Purpose | Audience |
|-----------|---------|----------|
| `dev/adr/` | Architecture Decision Records | Human + AI |
| `dev/commands/` | Reusable AI agent commands | AI agents |
| `dev/guidelines/` | Coding standards and conventions | Human + AI |
| `dev/guides/` | Step-by-step procedures | Human + AI |
| `dev/knowledge/` | Architecture explanations | Human + AI |
| `dev/prompts/` | Prompt templates for thinking tasks | Human |
| `dev/skills/` | Domain-specific AI agent skills | AI agents |

## Infrastructure

| Component | Local Port | Description |
|-----------|-----------|-------------|
| Infrahub | 8000 | Web UI + GraphQL API |
| Temporal | 7233 | gRPC endpoint |
| Temporal UI | 8080 | Web dashboard |
| SR Linux (gNMI) | 57400 | Per-device gNMI |
| Containerlab Graph | 50080 | Topology visualization |

## Lab Topology

3-node Nokia SR Linux spine-leaf fabric:
- `spine01` (IXR-D3, AS65000) — 4 fabric links
- `leaf01` (IXR-D2, AS65001) — 2 uplinks to spine
- `leaf02` (IXR-D2, AS65002) — 2 uplinks to spine
- Management: `172.20.20.0/24` (DHCP by Containerlab)
- Fabric underlay: `/31` point-to-point eBGP
