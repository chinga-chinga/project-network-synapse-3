"""Temporal activities for backing up device configurations."""

from temporalio import activity


@activity.defn
async def backup_running_config(device_hostname: str) -> str:
    """Backup the current running configuration from a device."""
    pass


@activity.defn
async def store_backup(device_hostname: str, config: str) -> None:
    """Store a configuration backup."""
    pass
