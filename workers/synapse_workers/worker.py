"""Temporal worker entry point."""

import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

# TODO: Import and register all workflow classes once implemented
# TODO: Import and register all activity functions once implemented


async def main() -> None:
    # TODO: Add TLS configuration for production Temporal server
    # TODO: Add namespace configuration (default: "default")
    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(temporal_address)

    worker = Worker(
        client,
        task_queue="network-changes",
        workflows=[],  # TODO: Register NetworkChangeWorkflow, DriftRemediationWorkflow, EmergencyChangeWorkflow
        activities=[],  # TODO: Register all activity functions from activities/
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
