# Backend Architecture

## Overview

The backend package (`network_synapse`) handles all interaction with Infrahub (Source of Truth), configuration generation, and network device management.

## Components

### Data Layer (`data/`)

- **`populate_sot.py`** — Seeds Infrahub with the full spine-leaf topology via GraphQL mutations. Supports idempotent upserts (get-or-create pattern). Dependency-ordered: manufacturer -> location -> platform -> device types -> ASNs -> namespace -> VRFs -> devices -> IPs -> interfaces -> BGP sessions.
- **`seed_data.yml`** — YAML inventory defining the entire lab topology: 3 Nokia SR Linux devices, 11 interfaces, 4 eBGP sessions, IP addressing scheme.

### Schema Layer (`schemas/`)

- **`load_schemas.py`** — Loads Infrahub schema extensions in dependency order via the `/api/schema/load` REST endpoint. Loads: VRF -> routing base -> routing BGP -> device extensions -> interface extensions.
- **Schema YAML files** — Extend Infrahub's built-in types with project-specific attributes (e.g., `management_ip`, `lab_node_name`, `asn` on DcimDevice).

### Scripts (`scripts/`)

- **`generate_configs.py`** — Renders Jinja2 templates into Nokia SR Linux JSON configurations suitable for gNMI deployment. Uses `FileSystemLoader` pointing to `templates/`.
- **`deploy_configs.py`** — (Stub) Will push generated configs to devices via pygnmi/gNMI.
- **`validate_configs.py`** — (Stub) Will validate post-deployment state via gNMI GET.

### Templates (`templates/`)

- **`srlinux_bgp.j2`** — Renders BGP configuration in SR Linux JSON-RPC/gNMI format.
- **`srlinux_interfaces.j2`** — Renders interface configuration in SR Linux JSON format.

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `infrahub-sdk` | Infrahub Python SDK for API interaction |
| `httpx` | HTTP client for REST/GraphQL calls |
| `jinja2` | Template rendering for SR Linux configs |
| `pyyaml` | YAML parsing for seed data and schemas |
| `pygnmi` | gNMI client for SR Linux device communication |
| `nornir` | Multi-device automation framework |
| `pydantic` | Data validation and settings management |

## Data Flow

```
seed_data.yml -> populate_sot.py -> Infrahub GraphQL API
                                          |
                                    (query device data)
                                          |
                              generate_configs.py + templates/
                                          |
                                    (SR Linux JSON configs)
                                          |
                              deploy_configs.py -> gNMI -> SR Linux devices
                                          |
                              validate_configs.py -> gNMI GET -> validation
```
