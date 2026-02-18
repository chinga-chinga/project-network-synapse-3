"""Temporal activities for interacting with Infrahub source of truth.

These activities run in Temporal's thread-pool executor, so synchronous
httpx calls (used by InfrahubConfigClient) are fine here.
"""

from __future__ import annotations

import os

from temporalio import activity

from network_synapse.infrahub.client import InfrahubConfigClient


@activity.defn
async def fetch_device_config(device_hostname: str) -> dict:
    """Fetch intended configuration for a device from Infrahub.

    Queries Infrahub GraphQL API for device metadata, interfaces, and BGP
    sessions.  Returns a dict with 'bgp' and 'interfaces' keys containing
    the template variable dicts ready for Jinja2 rendering.

    Returns:
        dict with keys:
            - hostname: device hostname
            - bgp: BGPTemplateVars as dict
            - interfaces: InterfacesTemplateVars as dict
    """
    client = InfrahubConfigClient(
        url=os.getenv("INFRAHUB_URL", "http://localhost:8000"),
        token=os.getenv("INFRAHUB_TOKEN", ""),
    )
    try:
        config = client.get_device_config(device_hostname)
        return {
            "hostname": device_hostname,
            "bgp": config.to_bgp_template_vars().model_dump(),
            "interfaces": config.to_interface_template_vars().model_dump(),
        }
    finally:
        client.close()


@activity.defn
async def update_device_status(device_hostname: str, status: str) -> None:
    """Update device status in Infrahub.

    TODO: Mutate device status field via Infrahub GraphQL
    TODO: Add audit log entry for status change
    """
