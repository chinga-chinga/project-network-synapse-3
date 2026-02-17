"""Placeholder integration tests — will test against Infrahub and Containerlab."""

import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="Integration tests not yet implemented — Week 3")
def test_infrahub_connection():
    """Test connectivity to Infrahub instance."""


@pytest.mark.integration
@pytest.mark.skip(reason="Integration tests not yet implemented — Week 3")
def test_containerlab_topology_running():
    """Test that Containerlab topology is deployed and reachable."""
