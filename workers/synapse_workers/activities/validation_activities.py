"""Temporal activities for post-deployment validation."""

from __future__ import annotations

from temporalio import activity

from network_synapse.scripts.validate_state import check_bgp_summary


@activity.defn
async def validate_bgp(device_hostname: str, ip_address: str) -> bool:
    """Validate BGP sessions are established on a device after deployment."""
    activity.logger.info(f"Validating BGP state on {device_hostname} ({ip_address})")
    result = check_bgp_summary(ip_address)
    if not result:
        raise RuntimeError(f"BGP validation failed on {device_hostname}")
    return True


@activity.defn
async def validate_interfaces(device_hostname: str, ip_address: str) -> bool:
    """Validate interface states match intended config.

    TODO: gNMI GET /interface[name=*] for oper-state, admin-state, IP
    TODO: Compare against Infrahub intended state
    TODO: Flag interfaces that are admin-up but oper-down
    """
    activity.logger.info(f"Interface validation for {device_hostname} — not yet implemented")
    return True
