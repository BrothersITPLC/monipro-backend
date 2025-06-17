import logging
from typing import Any, cast

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.item_functions import item_create_function
from zabbixproxy.models import HostLifecycle

celery_logger = logging.getLogger("celery")


@shared_task(bind=True, max_retries=3)
def item_creation_task(self, prev_task_result):
    """
    Celery task to create items for a host.
    Updates HostLifecycle status message on error.
    """
    params = prev_task_result.get("next_task_params", {})
    api_url = params.get("api_url")
    auth_token = params.get("auth_token")
    host_name = params.get("host_name")
    zabbix_host_hostid = params.get("zabbix_host_hostid")
    item_template_list = params.get("item_template_list")
    interface_id = params.get("interface_id")
    host_lifecycle_id = params.get("host_lifecycle_id")

    celery_logger.info(
        f"HostLifecycle ID: {host_lifecycle_id} - Attempting to create items for host '{host_name}'"
    )

    host_lifecycle = None
    try:
        host_lifecycle = HostLifecycle.objects.get(id=host_lifecycle_id)
    except HostLifecycle.DoesNotExist:
        error_msg = f"HostLifecycle with ID {host_lifecycle_id} not found in item_creation_task."
        celery_logger.critical(error_msg)
        raise ServiceErrorHandler(error_msg)
    except Exception as e:
        error_msg = f"Database error fetching HostLifecycle {host_lifecycle_id} in item_creation_task: {str(e)}"
        celery_logger.exception(error_msg)
        raise ServiceErrorHandler(error_msg)

    try:
        itemid_list = item_create_function(
            api_url,
            auth_token,
            host_name,
            zabbix_host_hostid,
            item_template_list,
            interface_id,
        )

        message = (
            f"Successfully created {len(itemid_list)} items for host '{host_name}'."
        )
        celery_logger.info(f"HostLifecycle ID: {host_lifecycle_id}: {message}")

        return {
            "status": "success",
            "message": message,
            "next_task_params": {
                "host_lifecycle_id": host_lifecycle_id,
            },
        }

    except ServiceErrorHandler as e:
        error_msg = f"Error creating Zabbix items for host '{host_name}': {str(e)}"
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for HostLifecycle {host_lifecycle_id} (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = f"Retrying item creation: {error_msg}"
                host_lifecycle.save()
            raise self.retry(countdown=5, exc=e)
        else:
            celery_logger.error(
                f"HostLifecycle {host_lifecycle_id} failed after retries: {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = error_msg
                host_lifecycle.save()
            raise ServiceErrorHandler(error_msg)

    except Exception as e:
        error_msg = (
            f"Unexpected error creating Zabbix items for host '{host_name}': {str(e)}"
        )
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for HostLifecycle {host_lifecycle_id} (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = (
                    f"Retrying item creation due to unexpected error: {error_msg}"
                )
                host_lifecycle.save()
            raise self.retry(countdown=5, exc=e)
        else:
            celery_logger.error(
                f"HostLifecycle {host_lifecycle_id} failed after retries due to unexpected error: {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = error_msg
                host_lifecycle.save()
            raise ServiceErrorHandler(error_msg)
