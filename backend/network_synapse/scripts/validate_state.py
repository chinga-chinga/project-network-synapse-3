"""Post-deployment state validation for Nokia SR Linux devices via gNMI."""

from __future__ import annotations

import logging
from typing import Any

from pygnmi.client import gNMIclient

logger = logging.getLogger(__name__)


def _extract_gnmi_val(result: dict) -> Any | None:
    """Extract the first 'val' payload from a gNMI GET response."""
    for notif in result.get("notification", []):
        for update in notif.get("update", []):
            if "val" in update:
                return update["val"]
    return None


def _evaluate_bgp_neighbors(ip_address: str, neighbors: Any) -> bool:
    """Parse a neighbor data block and verify all sessions are Established."""
    if not neighbors:
        logger.warning(f"No BGP neighbors found on {ip_address}")
        return False

    if isinstance(neighbors, list):
        peer_list = neighbors
    elif isinstance(neighbors, dict):
        peer_list = list(neighbors.values())
    else:
        logger.error(f"Unexpected data format from {ip_address}: {type(neighbors)}")
        return False

    all_ok = True
    for peer in peer_list:
        state = peer.get("session-state", "UNKNOWN")
        addr = peer.get("peer-address", "unknown")
        if state.lower() != "established":
            logger.error(f"BGP peer {addr} on {ip_address} is {state}")
            all_ok = False
        else:
            logger.info(f"BGP peer {addr} on {ip_address} is ESTABLISHED")
    return all_ok


def check_bgp_summary(
    ip_address: str,
    username: str = "admin",
    password: str = "NokiaSrl1!",  # noqa: S107
    port: int = 57400,
) -> bool:
    """Check if all configured BGP sessions are Established."""
    logger.info(f"Checking BGP state on {ip_address}")
    try:
        with gNMIclient(target=(ip_address, port), username=username, password=password, insecure=True) as gc:
            path = "/network-instance[name=default]/protocols/bgp/neighbor"
            result = gc.get(path=[path], datatype="state")

            neighbors = _extract_gnmi_val(result)
            if neighbors is not None:
                return _evaluate_bgp_neighbors(ip_address, neighbors)

            logger.error(f"No BGP state data found on {ip_address}")
            return False
    except Exception as e:
        logger.error(f"Failed to query {ip_address}: {e!s}")
        return False
