"""Temporal activities for interacting with Infrahub source of truth."""

from temporalio import activity


@activity.defn
async def fetch_device_config(device_hostname: str) -> dict:
    """Fetch intended configuration from Infrahub."""
    pass


@activity.defn
async def update_device_status(device_hostname: str, status: str) -> None:
    """Update device status in Infrahub."""
    pass
