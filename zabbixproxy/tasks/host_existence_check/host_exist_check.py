import logging
from typing import Any, Dict

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.functions.host_functions import check_host_exist
from zabbixproxy.models import HostLifecycle

celery_logger = logging.getLogger("celery")


@shared_task(bind=True, max_retries=3)
def check_host_existance_task(self, initial_task_params: Dict[str, Any]):
    """
    Celery task to check if a Zabbix host exists.
    If the host doesn't exist or an error occurs, the workflow stops by raising a ServiceErrorHandler.
    """

    api_url = initial_task_params.get("api_url")
    auth_token = initial_task_params.get("auth_token")
    host_id = initial_task_params.get("host_id")
    host_name = initial_task_params.get("host_name")
    host_lifecycle_id = initial_task_params.get("host_lifecycle_id")

    lifecycle_err_msg = f"Error while checking host with ID {host_id} existence. Please try again later."

    try:
        host_lifecycle = HostLifecycle.objects.get(pk=host_lifecycle_id)
    except HostLifecycle.DoesNotExist:
        host_lifecycle = None
        celery_logger.warning(f"HostLifecycle with ID {host_lifecycle_id} not found")

    try:
        celery_logger.info(
            f"HostLifecycle ID: {host_lifecycle_id} - Checking existence of host with ID: {host_id}"
        )

        host_exists = check_host_exist(
            api_url=api_url,
            auth_token=auth_token,
            host_name=host_name,
            host_id=host_id,
        )

        if host_exists:
            celery_logger.info(f"Host with ID {host_id} exists.")
            return {
                "status": "success",
                "message": f"Host with ID {host_id} exists.",
                "next_task_params": {
                    "api_url": api_url,
                    "auth_token": auth_token,
                    "host_id": host_id,
                    "host_name": host_name,
                    "host_lifecycle_id": host_lifecycle_id,
                },
            }

        if host_lifecycle:
            host_lifecycle.status = "deletion_failed"
            host_lifecycle.status_message = f"Host with ID {host_id} not found."
            host_lifecycle.save()

        raise ServiceErrorHandler(f"Host with ID {host_id} does not exist in Zabbix.")

    except ServiceErrorHandler as e:
        error_msg = str(e)
        retries = getattr(self.request, "retries", 0)

        if retries < self.max_retries and (
            "not authorized" in error_msg.lower()
            or "session terminated" in error_msg.lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for HostLifecycle {host_lifecycle_id} "
                f"(attempt {retries + 1}/{self.max_retries}) due to auth error: {error_msg}"
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
                f"Retrying task {self.request.id} for HostLifecycle {host_lifecycle_id} "
                f"(attempt {retries + 1}/{self.max_retries}) due to unexpected auth error: {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = lifecycle_err_msg
                host_lifecycle.save()
            raise self.retry(countdown=5, exc=e)
        else:
            celery_logger.error(
                f"HostLifecycle {host_lifecycle_id} failed due to unexpected error: {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status = "deletion_failed"
                host_lifecycle.status_message = lifecycle_err_msg
                host_lifecycle.save()
            raise ServiceErrorHandler(error_msg)
