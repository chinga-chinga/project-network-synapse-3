"""Temporal activities for post-deployment validation."""

from temporalio import activity


@activity.defn
async def validate_bgp(device_hostname: str) -> bool:
    """Validate BGP sessions are established."""
    pass


@activity.defn
async def validate_interfaces(device_hostname: str) -> bool:
    """Validate interface states match intended config."""
    pass
