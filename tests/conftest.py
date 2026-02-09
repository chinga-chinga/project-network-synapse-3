"""Shared test fixtures for the network automation project."""

import pytest


@pytest.fixture
def sample_device_data():
    """Sample device data matching Infrahub schema."""
    return {
        "name": "spine01",
        "device_type": "spine",
        "platform": "nokia_srlinux",
        "management_ip": "172.20.20.10",
        "asn": 65000,
        "role": "spine",
        "status": "active",
        "nos": "srlinux",
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
    """Full spine-leaf topology fixture (Nokia SR Linux)."""
    return {
        "spine01": {
            "asn": 65000,
            "mgmt_ip": "172.20.20.10",
            "role": "spine",
            "platform": "nokia_srlinux",
        },
        "leaf01": {
            "asn": 65001,
            "mgmt_ip": "172.20.20.11",
            "role": "leaf",
            "platform": "nokia_srlinux",
        },
        "leaf02": {
            "asn": 65002,
            "mgmt_ip": "172.20.20.12",
            "role": "leaf",
            "platform": "nokia_srlinux",
        },
    }
