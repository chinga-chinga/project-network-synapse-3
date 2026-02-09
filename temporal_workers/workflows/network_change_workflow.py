"""Workflow for standard network configuration changes."""

from temporalio import workflow


@workflow.defn
class NetworkChangeWorkflow:
    @workflow.run
    async def run(self, device_hostname: str) -> str:
        pass
