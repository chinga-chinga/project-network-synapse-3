# Running Tests

## Quick Start

```bash
# Run unit tests only (fast, no external deps)
uv run invoke backend.test-unit

# Run integration tests (requires Infrahub + Temporal + Containerlab)
uv run invoke backend.test-integration

# Run all tests with coverage
uv run invoke backend.test-all
```

## Direct pytest Usage

```bash
# Run a specific test file
uv run pytest tests/unit/test_placeholder.py -v

# Run tests matching a pattern
uv run pytest tests/ -k "bgp" -v

# Run with parallel execution
uv run pytest tests/unit/ -n auto

# Run with verbose output and no capture
uv run pytest tests/unit/ -v -s
```

## Test Markers

| Marker | Description | Command |
|--------|-------------|---------|
| `@pytest.mark.unit` | Fast, isolated tests | `pytest -m unit` |
| `@pytest.mark.integration` | Requires external services | `pytest -m integration` |
| `@pytest.mark.slow` | Tests taking >30 seconds | `pytest -m slow` |
| `@pytest.mark.pre_deployment` | Pre-deployment validation | `pytest -m pre_deployment` |
| `@pytest.mark.post_deployment` | Post-deployment validation | `pytest -m post_deployment` |

## Writing Tests

1. Place unit tests in `tests/unit/test_<module>.py`
2. Place integration tests in `tests/integration/test_<module>.py`
3. Use fixtures from `tests/conftest.py` for shared test data
4. Mark tests with appropriate markers
5. Use `pytest-asyncio` for async tests (auto mode enabled)

## Coverage

Coverage is configured in `pyproject.toml [tool.coverage]`. Reports cover:
- `backend/network_synapse/`
- `workers/synapse_workers/`
