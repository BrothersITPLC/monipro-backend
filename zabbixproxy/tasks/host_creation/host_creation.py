import logging
from typing import Any, Dict

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.functions.host_functions import host_creation
from zabbixproxy.models import Host, HostCredentials, HostLifecycle

celery_logger = logging.getLogger("celery")


@shared_task(bind=True, max_retries=3)
def host_creation_task(self, prev_task_result: Dict[str, Any]):
    """
    Celery task to create a Zabbix host.
    Expects host_lifecycle_id as input and passes it along.
    No longer creates HostLifecycle; HostLifecycle is created by the orchestrator task.
    """

    if "initial_task_params" in prev_task_result:
        initial_task_params = prev_task_result["initial_task_params"]
    else:
        initial_task_params = prev_task_result

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
        f"HostLifecycle ID: {host_lifecycle_id} - Creating host with parameters: hostgroup={hostgroup}, ip={ip}, dns={dns}, host={host_name} "
    )

    local_host_id = host_params.get("local_host_id")
    template_list = host_params.get("template_list")
    host_username = host_params.get("username", "")
    host_password = host_params.get("password", "")

    host_lifecycle = None
    lifecycle_err_msg = f"error while creating host for {host_name}, please try again"

    try:

        host_lifecycle = HostLifecycle.objects.get(id=host_lifecycle_id)

        host = Host.objects.get(pk=local_host_id)

        if host_username != "" and host_password != "":
            if not HostCredentials.objects.filter(host=host).exists():
                HostCredentials.objects.create(
                    host=host,
                    username=host_username,
                    password=host_password,
                )
                celery_logger.info(
                    f"HostCredentials created for Host ID: {local_host_id}"
                )
            else:
                celery_logger.info(
                    f"HostCredentials already exist for Host ID: {local_host_id}, skipping creation."
                )

    except HostLifecycle.DoesNotExist:
        error_msg = f"HostLifecycle with ID {host_lifecycle_id} not found in host_creationion_task."
        celery_logger.critical(error_msg)
        raise ServiceErrorHandler(error_msg)
    except Host.DoesNotExist:
        error_msg = f"Host with ID {local_host_id} not found for Zabbix host creation."
        celery_logger.error(error_msg)
        if host_lifecycle:
            host_lifecycle.status_message = lifecycle_err_msg
            host_lifecycle.save()
        raise ServiceErrorHandler(error_msg)
    except Exception as e:
        error_msg = f"Database error or unexpected issue during initial checks in host_creationion_task: {str(e)}"
        celery_logger.exception(error_msg)
        if host_lifecycle:
            host_lifecycle.status_message = lifecycle_err_msg
            host_lifecycle.save()
        raise ServiceErrorHandler(error_msg)

    try:
        zabbix_host_hostid = host_creation(
            api_url=api_url,
            auth_token=auth_token,
            hostgroup=hostgroup,
            host_name=host_name,
            template_list=template_list,
            ip=ip,
            port=port,
            dns=dns,
            useip=useip,
        )

        try:
            Host.objects.filter(pk=local_host_id).update(host_id=zabbix_host_hostid)
        except Exception as e:
            error_msg = f"Database error or unexpected issue during update in host_creationion_task: {str(e)}"
            celery_logger.exception(error_msg)
            if host_lifecycle:
                host_lifecycle.status_message = lifecycle_err_msg
                host_lifecycle.save()
            raise ServiceErrorHandler(error_msg)

        return {
            "status": "success",
            "message": f"Successfully created Zabbix host '{host_name}' with ID: {zabbix_host_hostid}",
        }

    except ServiceErrorHandler as e:
        error_msg = f"Error creating Zabbix host: {str(e)}"
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for HostLifecycle {host_lifecycle_id} (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = lifecycle_err_msg
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
        error_msg = f"Unexpected error creating host: {str(e)}"
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for HostLifecycle {host_lifecycle_id} (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = lifecycle_err_msg
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
