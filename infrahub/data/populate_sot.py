"""Seed data / initial population script for Infrahub source of truth."""

from infrahub_sdk import InfrahubClient


async def populate_devices(client: InfrahubClient) -> None:
    """Create initial network device entries in Infrahub."""
    pass


async def populate_interfaces(client: InfrahubClient) -> None:
    """Create initial interface entries in Infrahub."""
    pass


async def populate_bgp_sessions(client: InfrahubClient) -> None:
    """Create initial BGP session entries in Infrahub."""
    pass


async def main() -> None:
    client = await InfrahubClient.init()
    await populate_devices(client)
    await populate_interfaces(client)
    await populate_bgp_sessions(client)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
