import logging
from typing import Any, Dict

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.models import Host, HostLifecycle
from zabbixproxy.tasks.host_creation.agent_base_host_creation import (
    agent_base_host_creation_task,
)
from zabbixproxy.tasks.host_creation.host_creation import host_creation_task
from zabbixproxy.tasks.host_lifecycle_handlers import (
    update_host_lifecycle_status_failure_task,
    update_host_lifecycle_status_success_task,
)

celery_logger = logging.getLogger("celery")


@shared_task(bind=True)
def host_creation_workflow(
    self,
    host_name,
    ip,
    port,
    dns,
    useip,
    hostgroup,
    api_url,
    auth_token,
    host_params,
) -> Dict[str, Any]:
    """
    Orchestrates the entire host creation workflow and tracks status in the database.
    This task now creates the HostLifecycle object and manages the chain with handlers.
    """

    host_username = host_params.get("username")
    host_password = host_params.get("password")
    local_host_id = host_params.get("local_host_id")
    template_list = host_params.get("template_list")

    host_lifecycle = None
    host_lifecycle_id = None
    lifecycle_err_msg = f"error while creating host for {host_name}, please try again"

    try:
        host = Host.objects.get(pk=local_host_id)

        host_lifecycle = HostLifecycle.objects.create(
            host=host,
            status="creation_in_progress",
            status_message="Host creation workflow initiated and in progress.",
        )
        host_lifecycle_id = host_lifecycle.id
        celery_logger.info(
            f"HostLifecycle {host_lifecycle_id} created for host {host_name} with status 'creation_in_progress'."
        )

        initial_task_params = {
            "api_url": api_url,
            "auth_token": auth_token,
            "hostgroup": hostgroup,
            "host_name": host_name,
            "ip": ip,
            "port": port,
            "dns": dns,
            "useip": useip,
            "host_params": host_params,
            "host_lifecycle_id": host_lifecycle_id,
        }

        if host_username == "" or host_password == "":
            workflow_chain = (
                host_creation_task.s(initial_task_params)
                | update_host_lifecycle_status_success_task.s()
            )
        else:
            workflow_chain = (
                agent_base_host_creation_task.s(initial_task_params)
                | host_creation_task.s()
                | update_host_lifecycle_status_success_task.s()
            )

        error_handler_args = {
            "host_lifecycle_id": host_lifecycle_id,
        }

        workflow_chain.apply_async(
            link_error=update_host_lifecycle_status_failure_task.s(
                initial_params=error_handler_args
            )
        )

        celery_logger.info(
            f"Host creation workflow (HostLifecycle ID: {host_lifecycle_id}) chain launched for host {host_name}"
        )
        return {
            "status": "success",
            "message": f"Host creation workflow started for {host_name} (ID: {host_lifecycle_id})",
            "host_lifecycle_id": host_lifecycle_id,
        }

    except Host.DoesNotExist:
        error_msg = f"Host with ID {local_host_id} not found when starting workflow."
        celery_logger.error(error_msg)
        if host_lifecycle:
            host_lifecycle.status = "creation_failed"
            host_lifecycle.status_message = lifecycle_err_msg
            host_lifecycle.save()
        raise ServiceErrorHandler(error_msg)
    except ServiceErrorHandler as e:
        error_msg = f"Pre-workflow setup error: {str(e)}"
        celery_logger.error(error_msg)
        if host_lifecycle:
            host_lifecycle.status = "creation_failed"
            host_lifecycle.status_message = lifecycle_err_msg
            host_lifecycle.save()
        raise e
    except Exception as e:
        error_msg = f"Unexpected error setting up host creation workflow: {str(e)}"
        celery_logger.exception(error_msg)
        if host_lifecycle:
            host_lifecycle.status = "creation_failed"
            host_lifecycle.status_message = lifecycle_err_msg
            host_lifecycle.save()
        raise ServiceErrorHandler(error_msg)
