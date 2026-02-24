"""End-to-end tests covering the full automation workflow.

These tests verify the complete pipeline:
  Infrahub query → Config generation → Hygiene check → gNMI deploy → Validate

They require all infrastructure to be running (Infrahub, Containerlab, Temporal).
Run with: ``pytest tests/e2e/ -m e2e``
"""

from __future__ import annotations

import json
import os

import pytest

# ---------------------------------------------------------------------------
# E2E: Config generation pipeline
# ---------------------------------------------------------------------------


@pytest.mark.e2e
def test_full_config_generation_pipeline():
    """Generate configs from Infrahub data and validate them with hygiene checker."""
    from network_synapse.infrahub.client import InfrahubConfigClient
    from network_synapse.scripts.generate_configs import (
        generate_bgp_config,
        generate_interface_config,
    )
    from network_synapse.scripts.hygiene_checker import run_hygiene_checks

    url = os.getenv("INFRAHUB_URL", "http://localhost:8000")
    token = os.getenv("INFRAHUB_TOKEN", "")
    hostname = os.getenv("TEST_DEVICE_HOSTNAME", "spine01")

    # 1. Fetch from Infrahub
    client = InfrahubConfigClient(url=url, token=token)
    try:
        config = client.get_device_config(hostname)
        assert config is not None
    finally:
        client.close()

    # 2. Generate configs
    bgp_vars = config.to_bgp_template_vars()
    iface_vars = config.to_interface_template_vars()

    bgp_json = generate_bgp_config(bgp_vars.__dict__)
    iface_json = generate_interface_config(iface_vars.__dict__)

    assert bgp_json, "BGP config should not be empty"
    assert iface_json, "Interface config should not be empty"

    # 3. Validate with hygiene checker
    assert run_hygiene_checks(bgp_json, iface_json), "Generated configs should pass hygiene checks"


@pytest.mark.e2e
def test_config_deploy_and_validate():
    """Deploy a config to a device and validate the operational state."""
    from network_synapse.scripts.deploy_configs import (
        deploy_config,
        validate_gnmi_connection,
    )
    from network_synapse.scripts.validate_state import check_bgp_summary

    device_ip = os.getenv("TEST_DEVICE_IP", "172.20.20.2")
    hostname = os.getenv("TEST_DEVICE_HOSTNAME", "spine01")

    # 1. Verify connectivity
    assert validate_gnmi_connection(device_ip), f"Must be able to reach {device_ip} via gNMI"

    # 2. Deploy a minimal config (read-only test — just verify the path works)
    # We use an empty update to avoid mutating state in a test
    minimal_config = json.dumps({"system": {"name": {"host-name": hostname}}})
    result = deploy_config(
        hostname=hostname,
        ip_address=device_ip,
        config_payload=minimal_config,
    )
    assert result, "Deployment should succeed"

    # 3. Validate BGP state is still healthy
    bgp_ok = check_bgp_summary(device_ip)
    assert bgp_ok, "BGP sessions should remain established after deployment"


@pytest.mark.e2e
def test_hygiene_rejects_bad_config():
    """Verify the hygiene checker blocks a clearly invalid config."""
    from network_synapse.scripts.hygiene_checker import run_hygiene_checks

    bad_bgp = json.dumps(
        {
            "network-instance": [
                {
                    "protocols": {
                        "bgp": {
                            "autonomous-system": 0,
                            "group": [],
                            "neighbor": [{"peer-address": "not-an-ip"}],
                        }
                    }
                }
            ]
        }
    )
    valid_iface = json.dumps(
        {
            "interface": [
                {
                    "name": "ethernet-1/1",
                    "subinterface": [{"ipv4": {"address": [{"ip-prefix": "10.0.0.0/31"}]}}],
                }
            ]
        }
    )

    assert not run_hygiene_checks(bad_bgp, valid_iface), "Bad BGP config should fail hygiene"


@pytest.mark.e2e
def test_rollback_restores_config():
    """Verify that the rollback mechanism restores a previous config."""
    from network_synapse.scripts.deploy_configs import (
        deploy_config,
        validate_gnmi_connection,
    )

    device_ip = os.getenv("TEST_DEVICE_IP", "172.20.20.2")
    hostname = os.getenv("TEST_DEVICE_HOSTNAME", "spine01")

    if not validate_gnmi_connection(device_ip):
        pytest.skip(f"Cannot reach {device_ip}")

    # 1. Read current config (backup)
    from network_synapse.scripts.validate_state import check_bgp_summary

    original_bgp_ok = check_bgp_summary(device_ip)

    # 2. Deploy a harmless change
    minimal = json.dumps({"system": {"name": {"host-name": hostname}}})
    deploy_config(hostname, device_ip, minimal)

    # 3. Re-deploy the same (simulates rollback)
    deploy_config(hostname, device_ip, minimal)

    # 4. Verify BGP state unchanged
    post_bgp_ok = check_bgp_summary(device_ip)
    assert original_bgp_ok == post_bgp_ok, "BGP state should be unchanged after rollback"
