"""Temporal activities for backing up device configurations."""

from temporalio import activity

# TODO: Import pygnmi for gNMI GET operations
# TODO: Add backup storage backend (local filesystem, S3, or git)


@activity.defn
async def backup_running_config(device_hostname: str) -> str:
    """Backup the current running configuration from a device.

    TODO: gNMI GET / (full config tree) from SR Linux device
    TODO: Return config as JSON string
    TODO: Add timestamp and device metadata to backup
    """


@activity.defn
async def store_backup(device_hostname: str, config: str) -> None:
    """Store a configuration backup.

    TODO: Write backup to storage backend (filesystem/S3/git)
    TODO: Implement retention policy (keep last N backups)
    TODO: Add backup indexing for quick retrieval during rollback
    """
