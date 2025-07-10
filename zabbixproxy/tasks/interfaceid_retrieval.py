import logging
from typing import Any, cast

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.item_functions import get_interfaceid
from zabbixproxy.models import HostLifecycle

celery_logger = logging.getLogger("celery")


@shared_task(bind=True, max_retries=3)
def interfaceid_retrieval_task(self, prev_task_result):
    """
    Celery task to retrieve interfaceid for a host.
    Updates HostLifecycle status message on error.
    """
    params = prev_task_result.get("next_task_params", {})
    api_url = params.get("api_url")
    auth_token = params.get("auth_token")
    host_name = params.get("host_name")
    zabbix_host_hostid = params.get("zabbix_host_hostid")
    item_template_list = params.get("item_template_list")
    host_lifecycle_id = params.get("host_lifecycle_id")

    celery_logger.info(
        f"HostLifecycle ID: {host_lifecycle_id} - Attempting to get interfaceid for host {host_name} with hostid {zabbix_host_hostid}"
    )

    host_lifecycle = None
    try:
        host_lifecycle = HostLifecycle.objects.get(id=host_lifecycle_id)
    except HostLifecycle.DoesNotExist:
        error_msg = f"HostLifecycle with ID {host_lifecycle_id} not found in interfaceid_retrieval_task."
        celery_logger.critical(error_msg)
        raise ServiceErrorHandler(error_msg)
    except Exception as e:
        error_msg = f"Database error fetching HostLifecycle {host_lifecycle_id} in interfaceid_retrieval_task: {str(e)}"
        celery_logger.exception(error_msg)
        raise ServiceErrorHandler(error_msg)

    try:
        interfaceid = get_interfaceid(
            api_url,
            auth_token,
            zabbix_host_hostid,
            host_name,
        )

        celery_logger.info(
            f"HostLifecycle ID: {host_lifecycle_id}: Successfully retrieved interfaceid '{interfaceid}' for host '{host_name}'."
        )

        return {
            "status": "success",
            "message": f"Successfully retrieved interfaceid '{interfaceid}' for host '{host_name}'.",
            "next_task_params": {
                "api_url": api_url,
                "auth_token": auth_token,
                "host_name": host_name,
                "zabbix_host_hostid": zabbix_host_hostid,
                "interface_id": interfaceid,
                "item_template_list": item_template_list,
                "host_lifecycle_id": host_lifecycle_id,
            },
        }

    except ServiceErrorHandler as e:
        error_msg = f"Error retrieving interfaceid for host {host_name}: {str(e)}"
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for HostLifecycle {host_lifecycle_id} (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = (
                    f"Retrying interface ID retrieval: {error_msg}"
                )
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
            f"Unexpected error retrieving interfaceid for host {host_name}: {str(e)}"
        )
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for HostLifecycle {host_lifecycle_id} (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            if host_lifecycle:
                host_lifecycle.status_message = f"Retrying interface ID retrieval due to unexpected error: {error_msg}"
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
