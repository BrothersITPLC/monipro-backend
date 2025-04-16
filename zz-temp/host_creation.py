from typing import Any, Dict, Optional, cast

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.models import TaskStatus
from zabbixproxy.views.host_items.functions import create_host


@shared_task(bind=True, max_retries=3)
def create_zabbix_host_task(
    self,
    api_url: str,
    auth_token: str,
    hostgroup: str,
    host: str,
    ip: str,
    port: int,
    dns: str,
    useip: int,
    host_template: int,
    task_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Celery task to create a Zabbix host
    """
    # Update task status to in_progress
    task_status = None
    if task_id:
        try:
            task_status =cast(Any, TaskStatus).objects.get(task_id=task_id)
            task_status.update_status("in_progress")
        except cast(Any, TaskStatus).DoesNotExist:
            return {"success": "error", "message":f"Task with ID {task_id} not found"}

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
            host_template=host_template,
        )

        # Update task status
        if task_status:
            task_status.status = "completed"
            task_status.save()

        return {
            "status": "success",
            "hostid": hostid,
            "message":f"Successfully created Zabbix host '{host}' with ID: {hostid}"
        }

    except ServiceErrorHandler as e:
        error_msg = f"Error creating Zabbix host: {str(e)}"

        # Update task status
        if task_status:
            task_status.status = "failed"
            task_status.error_message = error_msg
            task_status.save()

        # Retry if it's an authentication error
        if "not authorized" in str(e).lower() or "session terminated" in str(e).lower():
            if self.request.retries < self.max_retries:
                return self.retry(countdown=5)

        return {"status":"error", "message": error_msg}

    except Exception as e:
        error_msg = f"Error creating Zabbix host: {str(e)}"
        # Update task status
        if task_status:
            task_status.status = "failed"
            task_status.error_message = error_msg
            task_status.save()

        # Retry for unexpected errors
        if self.request.retries < self.max_retries:
            return self.retry(countdown=5)

        return {"status": "error", "message": error_msg}