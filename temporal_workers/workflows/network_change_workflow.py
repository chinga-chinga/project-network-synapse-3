"""Workflow for standard network configuration changes."""

from temporalio import workflow

# TODO: Import activity stubs for use in workflow steps


@workflow.defn
class NetworkChangeWorkflow:
    """Standard network change: backup -> generate config -> deploy -> validate.

    TODO: Implement full workflow sequence:
      1. Backup current running config (device_backup_activities)
      2. Fetch intended config from Infrahub (infrahub_activities)
      3. Generate SR Linux JSON config (render Jinja2 templates)
      4. Deploy config via gNMI (config_deployment_activities)
      5. Validate post-deploy state (validation_activities)
      6. Rollback on validation failure
    TODO: Add human-approval signal for production changes
    TODO: Add change-window enforcement (maintenance window check)
    """

    @workflow.run
    async def run(self, device_hostname: str) -> str:
        pass
