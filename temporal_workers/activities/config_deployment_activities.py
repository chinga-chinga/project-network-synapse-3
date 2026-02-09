"""Temporal activities for deploying configurations to network devices."""

from temporalio import activity


@activity.defn
async def deploy_config(device_hostname: str, config: str) -> bool:
    """Deploy configuration to a network device."""
    pass


@activity.defn
async def rollback_config(device_hostname: str) -> bool:
    """Rollback device to previous configuration."""
    pass
