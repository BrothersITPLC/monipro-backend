import logging
from typing import Any, Dict

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.functions.host_functions import delete_host
from zabbixproxy.models import HostLifecycle

celery_logger = logging.getLogger("celery")


@shared_task(bind=True, max_retries=3)
def host_deletion_task(self, prev_task_output: Dict[str, Any]):
    """
    Celery task to delete a Zabbix host.
    """
    next_params = prev_task_output.get("next_task_params", {})
    api_url = next_params.get("api_url")
    auth_token = next_params.get("auth_token")
    host_id = next_params.get("host_id")
    host_lifecycle_id = next_params.get("host_lifecycle_id")

    lifecycle_err_msg = (
        f"Error while deleting host with ID {host_id}. Please try again later."
    )

    try:
        host_lifecycle = HostLifecycle.objects.get(pk=host_lifecycle_id)
    except HostLifecycle.DoesNotExist:
        host_lifecycle = None
        celery_logger.warning(f"HostLifecycle with ID {host_lifecycle_id} not found")

    try:
        celery_logger.info(
            f"HostLifecycle ID {host_lifecycle_id}: Deleting host ID {host_id}"
        )

        deleted = delete_host(api_url, auth_token, host_id)

        if deleted:
            if host_lifecycle:
                host_lifecycle.status = "inactive"
                host_lifecycle.status_message = (
                    f"Host ID {host_id} deleted successfully."
                )
                host_lifecycle.save()

            return {
                "status": "success",
                "message": f"Host ID {host_id} deleted.",
            }

        if host_lifecycle:
            host_lifecycle.status = "deletion_failed"
            host_lifecycle.status_message = f"Host ID {host_id} deletion unsuccessful."
            host_lifecycle.save()

        raise ServiceErrorHandler(
            f"Zabbix did not confirm deletion of host ID {host_id}."
        )

    except ServiceErrorHandler as e:
        retries = getattr(self.request, "retries", 0)
        error_msg = str(e)

        if retries < self.max_retries and (
            "not authorized" in error_msg.lower()
            or "session terminated" in error_msg.lower()
        ):
            celery_logger.warning(
                f"Retrying deletion task for HostLifecycle {host_lifecycle_id} (attempt {retries + 1}): {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = lifecycle_err_msg
                host_lifecycle.save()
            raise self.retry(countdown=5, exc=e)

        celery_logger.error(
            f"HostLifecycle {host_lifecycle_id} deletion failed: {error_msg}"
        )
        if host_lifecycle:
            host_lifecycle.status = "deletion_failed"
            host_lifecycle.status_message = lifecycle_err_msg
            host_lifecycle.save()

        raise ServiceErrorHandler(error_msg)

    except Exception as e:
        error_msg = str(e)
        retries = getattr(self.request, "retries", 0)

        if retries < self.max_retries and (
            "not authorized" in error_msg.lower()
            or "session terminated" in error_msg.lower()
        ):
            celery_logger.warning(
                f"Retrying deletion task for HostLifecycle {host_lifecycle_id} (attempt {retries + 1}): {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = lifecycle_err_msg
                host_lifecycle.save()
            raise self.retry(countdown=5, exc=e)

        celery_logger.error(
            f"HostLifecycle {host_lifecycle_id} deletion failed: {error_msg}"
        )
        if host_lifecycle:
            host_lifecycle.status = "deletion_failed"
            host_lifecycle.status_message = lifecycle_err_msg
            host_lifecycle.save()

        raise ServiceErrorHandler(error_msg)
