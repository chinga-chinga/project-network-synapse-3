"""Shared test fixtures for the network automation project."""

import os

import pytest

# ─── Containerlab mgmt IPs (DHCP-assigned, may change on redeploy) ───
# Current assignment on synapse-vm-01:
#   leaf01:  172.20.20.2
#   spine01: 172.20.20.3
#   leaf02:  172.20.20.4
# For integration tests, use the clab_topology fixture below.
# For unit tests, fixtures use stable placeholder IPs (mocked, not real).


@pytest.fixture
def sample_device_data():
    """Sample device data matching Infrahub schema (unit tests — mocked)."""
    return {
        "name": "spine01",
        "device_type": "7220 IXR-D3",
        "platform": "nokia_srlinux",
        "management_ip": "172.20.20.3",
        "asn": 65000,
        "role": "spine",
        "status": "active",
        "nos": "srlinux",
        "sw_version": "v25.10.1",
    }


@pytest.fixture
def sample_bgp_session():
    """Sample BGP session data (SR Linux style)."""
    return {
        "local_asn": 65000,
        "remote_asn": 65001,
        "local_ip": "10.0.0.0",
        "remote_ip": "10.0.0.1",
        "description": "spine01 to leaf01",
        "status": "active",
        "network_instance": "default",
        "group": "underlay",
    }


@pytest.fixture
def spine_leaf_topology():
    """Full spine-leaf topology fixture (Nokia SR Linux — unit tests)."""
    return {
        "spine01": {
            "asn": 65000,
            "mgmt_ip": "172.20.20.3",
            "role": "spine",
            "platform": "nokia_srlinux",
            "type": "ixr-d3",
        },
        "leaf01": {
            "asn": 65001,
            "mgmt_ip": "172.20.20.2",
            "role": "leaf",
            "platform": "nokia_srlinux",
            "type": "ixr-d2",
        },
        "leaf02": {
            "asn": 65002,
            "mgmt_ip": "172.20.20.4",
            "role": "leaf",
            "platform": "nokia_srlinux",
            "type": "ixr-d2",
        },
    }


@pytest.fixture
def clab_credentials():
    """SR Linux default credentials for Containerlab nodes."""
    return {
        "username": os.getenv("SRLINUX_USER", "admin"),
        "password": os.getenv("SRLINUX_PASS", "NokiaSrl1!"),
        "gnmi_port": 57400,
        "jsonrpc_port": 443,
    }
