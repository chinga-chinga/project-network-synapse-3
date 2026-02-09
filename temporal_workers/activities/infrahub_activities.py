"""Temporal activities for interacting with Infrahub source of truth."""

import os

from temporalio import activity

# TODO: Initialize InfrahubClient with env-based config
# INFRAHUB_ADDRESS = os.getenv("INFRAHUB_ADDRESS", "http://localhost:8080")


@activity.defn
async def fetch_device_config(device_hostname: str) -> dict:
    """Fetch intended configuration from Infrahub.

    TODO: Query Infrahub GraphQL API for device + interfaces + BGP sessions
    TODO: Return structured dict matching Jinja2 template variables
    TODO: Handle device-not-found and connection errors gracefully
    """
    pass


@activity.defn
async def update_device_status(device_hostname: str, status: str) -> None:
    """Update device status in Infrahub.

    TODO: Mutate device status field via Infrahub SDK
    TODO: Add audit log entry for status change
    """
    pass
