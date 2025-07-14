import logging

from celery import shared_task

celery_logger = logging.getLogger("celery")

from utils import ServiceErrorHandler
from zabbixproxy.models import Host, HostLifecycle
from zabbixproxy.tasks.host_deletion.host_deletion import host_deletion_task
from zabbixproxy.tasks.host_existence_check import check_host_existance_task


@shared_task(bind=True)
def host_deletion_workflow(
    self,
    api_url,
    auth_token,
    host_id,
    local_host_id,
):
    """
    Orchestrates the host deletion workflow and tracks status in the HostLifecycle model.
    """

    try:
        host_lifecycle = HostLifecycle.objects.get(host__id=local_host_id)
    except HostLifecycle.DoesNotExist:
        celery_logger.error(
            f"HostLifecycle record for host ID {local_host_id} not found."
        )
        raise ServiceErrorHandler(
            f"HostLifecycle record for host ID {local_host_id} not found."
        )

    host_lifecycle.status = "deletion_in_progress"
    host_lifecycle.status_message = "Host deletion workflow initiated and in progress."
    host_lifecycle.save()

    host_lifecycle_id = host_lifecycle.id

    initial_task_params = {
        "api_url": api_url,
        "auth_token": auth_token,
        "host_id": host_id,
        "host_lifecycle_id": host_lifecycle_id,
        "host_name": "",
    }

    try:
        workflow_chain = (
            check_host_existance_task.s(initial_task_params) | host_deletion_task.s()
        )

        workflow_chain.delay()
        celery_logger.info(
            f"Host deletion workflow chain started for host ID {host_id}"
        )

    except Exception as e:
        error_msg = f"Failed to start host deletion workflow: {e}"
        celery_logger.error(error_msg)
        host_lifecycle.status = "deletion_failed"
        host_lifecycle.status_message = error_msg
        host_lifecycle.save()
        raise ServiceErrorHandler(error_msg)
