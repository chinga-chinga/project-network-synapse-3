"""Temporal activities for deploying configurations to network devices."""

from temporalio import activity

# TODO: Import pygnmi for gNMI SET operations
# TODO: Add device credential management (env vars or vault)


@activity.defn
async def deploy_config(device_hostname: str, config: str) -> bool:
    """Deploy configuration to a network device.

    TODO: Resolve hostname to management IP (from Infrahub or DNS)
    TODO: Connect via gNMI and apply SR Linux JSON config with SET
    TODO: Add config diff logging before apply
    TODO: Handle connection timeouts and partial failures
    """
    pass


@activity.defn
async def rollback_config(device_hostname: str) -> bool:
    """Rollback device to previous configuration.

    TODO: Retrieve stored backup config
    TODO: Apply backup via gNMI SET (replace operation)
    TODO: Validate state after rollback
    """
    pass
