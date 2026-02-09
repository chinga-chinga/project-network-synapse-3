"""Seed data / initial population script for Infrahub source of truth."""

# TODO: Read seed data from YAML/JSON files instead of hardcoding
# TODO: Add idempotency — skip objects that already exist
# TODO: Match topology to containerlab/topology.clab.yml (spine01, leaf01, leaf02)

from infrahub_sdk import InfrahubClient


async def populate_devices(client: InfrahubClient) -> None:
    """Create initial network device entries in Infrahub.

    TODO: Create spine01 (ixrd3), leaf01 (ixrd2), leaf02 (ixrd2)
    TODO: Set platform=nokia_srlinux, management IPs from clab mgmt network
    TODO: Set ASNs: spine=65000, leaf01=65001, leaf02=65002
    """
    pass


async def populate_interfaces(client: InfrahubClient) -> None:
    """Create initial interface entries in Infrahub.

    TODO: Create spine01:e1-1..e1-4, leaf01:e1-49..e1-50, leaf02:e1-49..e1-50
    TODO: Assign p2p /31 addresses for fabric links
    TODO: Create loopback0 interfaces with /32 addresses
    """
    pass


async def populate_bgp_sessions(client: InfrahubClient) -> None:
    """Create initial BGP session entries in Infrahub.

    TODO: Create eBGP sessions between spine01 and each leaf
    TODO: Set session type, peer group, local/remote ASN and IPs
    TODO: Use "underlay" peer group for fabric sessions
    """
    pass


async def main() -> None:
    client = await InfrahubClient.init()
    await populate_devices(client)
    await populate_interfaces(client)
    await populate_bgp_sessions(client)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
