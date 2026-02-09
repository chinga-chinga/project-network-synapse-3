"""Workflow for emergency network changes with expedited approval."""

from temporalio import workflow


@workflow.defn
class EmergencyChangeWorkflow:
    @workflow.run
    async def run(self, device_hostname: str) -> str:
        pass
