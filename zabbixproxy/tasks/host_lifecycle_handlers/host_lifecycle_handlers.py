import logging

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.models import HostLifecycle

celery_logger = logging.getLogger("celery")


@shared_task
def update_host_lifecycle_status_success_task(result_from_prev_task: dict):
    """
    Final task in the chain to update HostLifecycle status to 'active'.
    Receives the 'next_task_params' dict from the preceding successful task.
    """
    host_lifecycle_id = result_from_prev_task.get("next_task_params", {}).get(
        "host_lifecycle_id"
    )
    success_message = result_from_prev_task.get(
        "message", "Host creation completed successfully."
    )

    if not host_lifecycle_id:
        celery_logger.error(
            f"Success handler: host_lifecycle_id not found in result from previous task: {result_from_prev_task}"
        )
        return

    try:
        host_lifecycle = HostLifecycle.objects.get(id=host_lifecycle_id)
        host_lifecycle.status = "active"
        host_lifecycle.status_message = success_message
        host_lifecycle.save()
        celery_logger.info(
            f"HostLifecycle {host_lifecycle_id} status updated to 'active'. Message: {success_message}"
        )
    except HostLifecycle.DoesNotExist:
        celery_logger.error(
            f"HostLifecycle with ID {host_lifecycle_id} not found for success update. It might have been deleted."
        )
    except Exception as e:
        celery_logger.exception(
            f"Error updating HostLifecycle {host_lifecycle_id} to active: {e}"
        )


@shared_task
def update_host_lifecycle_status_failure_task(
    task_id: str, exc: Exception, traceback: str, initial_params: dict
):
    """
    Error handler task for the host creation workflow.
    `initial_params` is a dictionary passed by the orchestrator, containing host_lifecycle_id.
    """
    host_lifecycle_id = initial_params.get("host_lifecycle_id")
    err_message = (
        "An unknown error occurred during host creation.please try again later."
    )

    if isinstance(exc, ServiceErrorHandler):
        error_message = str(exc)
    else:
        celery_logger.error(
            f"Unhandled exception in task {task_id}: {exc}\n{traceback}"
        )
        error_message = f"An unexpected system error occurred during host creation: {type(exc).__name__}."

    if not host_lifecycle_id:
        celery_logger.error(
            f"Failure handler: host_lifecycle_id not found in initial_params: {initial_params}. Task ID: {task_id}. Original exception: {exc}"
        )
        return

    try:
        host_lifecycle = HostLifecycle.objects.get(id=host_lifecycle_id)
        host_lifecycle.status = "creation_failed"
        host_lifecycle.status_message = err_message
        host_lifecycle.save()
        celery_logger.error(
            f"HostLifecycle {host_lifecycle_id} status updated to 'creation_failed'. Message: {error_message}"
        )
    except HostLifecycle.DoesNotExist:
        celery_logger.error(
            f"HostLifecycle with ID {host_lifecycle_id} not found for failure update. It might have been deleted."
        )
    except Exception as e:
        celery_logger.exception(
            f"Error updating HostLifecycle {host_lifecycle_id} to failed: {e}"
        )
