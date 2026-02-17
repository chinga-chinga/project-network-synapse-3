"""Temporal activities for post-deployment validation."""

from temporalio import activity

# TODO: Import pygnmi for gNMI GET operations


@activity.defn
async def validate_bgp(device_hostname: str) -> bool:
    """Validate BGP sessions are established.

    TODO: gNMI GET /network-instance[name=default]/protocols/bgp/neighbor
    TODO: Check each neighbor session-state == "established"
    TODO: Return structured result with per-neighbor details
    TODO: Add configurable timeout for BGP convergence wait
    """


@activity.defn
async def validate_interfaces(device_hostname: str) -> bool:
    """Validate interface states match intended config.

    TODO: gNMI GET /interface[name=*] for oper-state, admin-state, IP
    TODO: Compare against Infrahub intended state
    TODO: Flag interfaces that are admin-up but oper-down
    """
