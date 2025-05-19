import logging
from typing import Any, cast

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.host_functions import create_host
from zabbixproxy.models import TaskStatus

django_logger = logging.getLogger("django")


@shared_task(bind=True, max_retries=3)
def create_zabbix_host_task(
    self,
    prev_task_result,  # Accept previous task's result as first argument
):
    """
    Celery task to create a Zabbix host
    """
    # Extract parameters from previous task result

    params = prev_task_result.get("next_task_params", {})
    api_url = params.get("api_url")
    auth_token = params.get("auth_token")
    hostgroup = params.get("hostgroup")
    host = params.get("host")
    ip = params.get("ip")
    port = params.get("port")
    dns = params.get("dns")
    useip = params.get("useip")
    task_id = params.get("task_id")
    record_task_id = params.get("record_task_id")
    device_type = params.get("device_type")
    network_device_type = params.get("network_device_type")
    username = params.get("username")
    password = params.get("password")
    django_logger.info(
        f"Creating host with parameters: hostgroup={hostgroup}, hostid={ip}, host={host}"
    )

    task_status = None
    if task_id:
        try:
            task_status = cast(Any, TaskStatus).objects.get(task_id=task_id)
            task_status.update_status("in_progress")
        except cast(Any, TaskStatus).DoesNotExist:
            return {"status": "error", "message": f"Task with ID {task_id} not found"}

    try:
        hostid = create_host(
            api_url,
            auth_token,
            hostgroup=hostgroup,
            host=host,
            ip=ip,
            port=port,
            dns=dns,
            useip=useip,
        )

        if task_status:
            task_status.status = "completed"
            task_status.save()

        return {
            "status": "success",
            "next_task_params": {
                "hostgroup": hostgroup,
                "hostid": hostid,
                "host": host,
                "ip": ip,
                "port": port,
                "dns": dns,
                "device_type": device_type,
                "network_device_type": network_device_type,
                "username": username,
                "password": password,
                "message": f"Successfully created Zabbix host '{host}' with ID: {hostid}",
            },
        }

    except ServiceErrorHandler as e:
        error_msg = f"Error creating Zabbix host: {str(e)}"

        if task_status:
            task_status.status = "failed"
            task_status.error_message = error_msg
            task_status.save()

        if "not authorized" in str(e).lower() or "session terminated" in str(e).lower():
            if self.request.retries < self.max_retries:
                return self.retry(countdown=5)

        return {"status": "error", "message": error_msg}

    except Exception as e:
        error_msg = f"Error creating Zabbix host: {str(e)}"
        if task_status:
            task_status.status = "failed"
            task_status.error_message = error_msg
            task_status.save()

        if self.request.retries < self.max_retries:
            return self.retry(countdown=5)

        return {"status": "error", "message": error_msg}
