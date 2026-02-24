# Week 3 Implementation Plan: Deployment & Validation

This plan outlines the execution strategy for the 7 issues comprising the "Week 3: Deployment + Validation" milestone. We will tackle these sequentially, ensuring that the deployment mechanisms are rock solid before layering on the validation and observability checks.

## Architectural Decisions

- **Deployment Mechanism**: We will build out native Python `gNMI` operations using the `pygnmi` library within the Temporal worker framework. This replaces the need for an external Ansible playbook and provides faster, more robust deployment with strict error handling.
- **Network Telemetry**: We will use **Suzieq** over InfluxDB/Telegraf due to its ease of implementation for snapshot-based CLI network introspection. It requires zero configuration on the switches themselves.

## Proposed Changes

### 1. Issue #18 & #19: Config Deployment Mechanism

We will implement the deployment mechanism to push JSON configuration from the backend out to the Nokia SR Linux nodes.

#### [MODIFY] [deploy_configs.py](file:///Users/anton/PYPROJECTS/project-network-synapse-3/backend/network_synapse/scripts/deploy_configs.py)

Implement `pygnmi` SET operations to push the Jinja2-rendered JSON files to the devices over gNMI.

#### [MODIFY] [network_change_workflow.py](file:///Users/anton/PYPROJECTS/project-network-synapse-3/workers/synapse_workers/workflows/network_change_workflow.py)

Flesh out the Temporal workflow to invoke the generation and deployment scripts using proper Temporal Activities.

---

### 2. Issue #21 & #22: Integration Testing & Post-Deployment Validation

We will implement real End-to-End checks to prove the deployed configs actually took effect in the lab.

#### [MODIFY] [test_placeholder.py](file:///Users/anton/PYPROJECTS/project-network-synapse-3/tests/integration/test_placeholder.py)

Replace stubs with actual integration tests that:

- Connect to `infrahub` and verify the data.
- Connect to `Containerlab` (via PyGNMI) and verify operational state.

#### [NEW] `backend/network_synapse/scripts/validate_state.py`

A new script to perform post-deployment checks (e.g., asserting BGP sessions are `established` and interfaces are `up`).

---

### 3. Issue #23: Configuration Hygiene

#### [NEW] `backend/network_synapse/scripts/hygiene_checker.py`

We will build a pre-deployment gate that analyzes the generated JSON structures to ensure they meet basic logic requirements (e.g. no empty BGP groups, proper ASNs, valid IP subnets) before allowing a deployment.

---

### 4. Issue #20 & 24: Observability and Telemetry

#### [MODIFY] [docker-compose-deps.yml](file:///Users/anton/PYPROJECTS/project-network-synapse-3/development/docker-compose-deps.yml)

We will add `Prometheus` and `Alertmanager` to the docker-compose stack.

#### [NEW] `development/prometheus/alert_rules.yml`

Define the critical network failure scenario alerts (BGP down, node unreachable).

## Verification Plan

### Automated Tests

1. **Config Generation Tests:** `uv run invoke backend.test-unit`
2. **Integration Tests:** `uv run invoke backend.test-integration`
   - These will connect to the live GCP VM's Infrahub instance and Containerlab nodes to perform E2E deployment tests to ensure the implementation works.
3. **Pre-commit Checks:** `uv run invoke check-all` to ensure no linting/security regressions.

### Manual Verification

1. Running the Temporal workflow manually via a starter script to watch the orchestration UI complete the `[Generate] -> [Deploy] -> [Validate]` pipeline successfully on the running GCP VM.
