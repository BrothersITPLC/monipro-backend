import logging
import re
from typing import Any, Dict, Optional, cast

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.functions.automation_functions.ansibal_runner import (
    create_zabbix_agent,
)
from zabbixproxy.models import Host, HostLifecycle

celery_logger = logging.getLogger("celery")


@shared_task(bind=True, max_retries=3)
def agent_base_host_creation_task(
    self,
    initial_task_params,
) -> Dict[str, Any]:
    """
    Celery task to deploy Zabbix agent using Ansible.
    It passes required parameters to the next task (Zabbix host creation).
    It now handles HostLifecycle updates directly.
    """

    api_url = initial_task_params.get("api_url")
    auth_token = initial_task_params.get("auth_token")
    hostgroup = initial_task_params.get("hostgroup")
    host_name = initial_task_params.get("host_name")
    ip = initial_task_params.get("ip")
    port = initial_task_params.get("port")
    dns = initial_task_params.get("dns")
    useip = initial_task_params.get("useip")
    host_params = initial_task_params.get("host_params")
    host_lifecycle_id = initial_task_params.get("host_lifecycle_id")

    celery_logger.info(
        f"HostLifecycle ID: {host_lifecycle_id} - Initiating agent deployment for host: {host_name} ({ip})"
    )

    host_username = host_params.get("username")
    host_password = host_params.get("password")
    local_host_id = host_params.get("local_host_id")
    target_host = ip if useip else dns

    host_lifecycle = None
    lifecycle_err_msg = f"error while creating host for {host_name}, please try again"

    try:
        host_lifecycle = HostLifecycle.objects.get(id=host_lifecycle_id)

        host = Host.objects.get(pk=local_host_id)

    except HostLifecycle.DoesNotExist:
        error_msg = f"HostLifecycle with ID {host_lifecycle_id} not found in agent_base_host_creation_task."
        celery_logger.critical(error_msg)
        raise ServiceErrorHandler(error_msg)
    except Host.DoesNotExist:
        error_msg = (
            f"Host with ID {local_host_id} not found for Zabbix agent deployment."
        )
        celery_logger.error(error_msg)
        if host_lifecycle:
            host_lifecycle.status_message = lifecycle_err_msg
            host_lifecycle.save()
        raise ServiceErrorHandler(error_msg)
    except Exception as e:
        error_msg = f"Database error or unexpected issue during initial checks in agent_base_host_creation_task: {str(e)}"
        celery_logger.exception(error_msg)
        if host_lifecycle:
            host_lifecycle.status_message = lifecycle_err_msg
            host_lifecycle.save()
        raise ServiceErrorHandler(error_msg)

    try:

        agent_response = create_zabbix_agent(
            port=port,
            target_host=target_host,
            username=host_username,
            hostname=host_name,
            password=host_password,
            tags="install",
        )

        overall_success = agent_response.get("overall_success", False)
        unsuccessfully_executed_tasks = agent_response.get(
            "unsuccessfully_executed_tasks", []
        )
        error_details = []

        if not overall_success:
            if unsuccessfully_executed_tasks:
                for error in unsuccessfully_executed_tasks:
                    error_details.append(
                        f"{error.get('task', 'Unknown task')}: {error.get('details', 'No details')}"
                    )
                error_msg = "Zabbix agent deployment failed: " + "; ".join(
                    error_details
                )
            else:
                error_msg = "Zabbix agent deployment failed with unknown reason."

            celery_logger.error(f"HostLifecycle {host_lifecycle_id}: {error_msg}")
            if host_lifecycle:
                host_lifecycle.status_message = lifecycle_err_msg
                host_lifecycle.save()
            raise ServiceErrorHandler(error_msg)

        celery_logger.info(
            f"HostLifecycle {host_lifecycle_id}: Zabbix agent deployed successfully for host '{host_name}'."
        )

        return {
            "status": "success",
            "message": f"Successfully deployed Zabbix agent for host '{host_name}'.",
            "initial_task_params": {
                "api_url": api_url,
                "auth_token": auth_token,
                "host_name": host_name,
                "hostgroup": hostgroup,
                "ip": ip,
                "port": port,
                "dns": dns,
                "useip": useip,
                "host_params": host_params,
                "host_lifecycle_id": host_lifecycle_id,
            },
        }

    except ServiceErrorHandler as e:
        error_msg = (
            f"Error in agent_base_host_creation_task (agent deployment): {str(e)}"
        )
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for HostLifecycle {host_lifecycle_id} (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = (
                    f"Retrying agent deployment: {error_msg}"
                )
                host_lifecycle.save()
            raise self.retry(countdown=5, exc=e)
        else:
            celery_logger.error(
                f"HostLifecycle {host_lifecycle_id} failed after retries: {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = lifecycle_err_msg
                host_lifecycle.save()
            raise ServiceErrorHandler(error_msg)

    except Exception as e:
        error_msg = f"Unexpected error in agent_base_host_creation_task (agent deployment): {str(e)}"
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for HostLifecycle {host_lifecycle_id} (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = (
                    f"Retrying agent deployment due to unexpected error: {error_msg}"
                )
                host_lifecycle.save()
            raise self.retry(countdown=5, exc=e)
        else:
            celery_logger.error(
                f"HostLifecycle {host_lifecycle_id} failed after retries due to unexpected error: {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = lifecycle_err_msg
                host_lifecycle.save()
            raise ServiceErrorHandler(error_msg)
