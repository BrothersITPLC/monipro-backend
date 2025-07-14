import logging

from celery import shared_task

celery_logger = logging.getLogger("celery")
from utils import ServiceErrorHandler
from zabbixproxy.functions.template_functions import creat_template_group
from zabbixproxy.models import TemplateGroupMirror


@shared_task(bind=True, max_retries=3)
def create_zabbix_template_group(
    self,
    api_url,
    auth_token,
    temp_group_name,
):
    """
    Celery task to create a Zabbix template group.
    """
    if not api_url or not auth_token or not temp_group_name:
        celery_logger.error("missing required parameters for template group creation")
        raise ServiceErrorHandler(
            "Missing required parameters for template group creation"
        )
    try:
        template_group_id = creat_template_group(
            api_url=api_url,
            auth_token=auth_token,
            temp_group_name=temp_group_name,
        )

        if template_group_id:
            try:
                template_group_instance = TemplateGroupMirror.objects.get(
                    template_group_name=temp_group_name
                ).first()
                template_group_instance.template_group_id = template_group_id
                template_group_instance.save()
                return {
                    "status": "success",
                    "message": f"Successfully created Zabbix template group '{temp_group_name}' with ID: {template_group_id}",
                }
            except TemplateGroupMirror.DoesNotExist:
                celery_logger.error(
                    f"Template group with this name {temp_group_name} not found in the database"
                )
                raise ServiceErrorHandler(
                    f"Template group with this name {temp_group_name} not found in the database"
                )

    except ServiceErrorHandler as e:
        error_msg = f"Error creating Zabbix Template group: {str(e)}"
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for TemplateGroupMirror (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            raise self.retry(countdown=5, exc=e)
        else:
            celery_logger.error(
                f"TemplateGroupMirror failed after retries: {error_msg}"
            )
            raise ServiceErrorHandler(error_msg)

    except Exception as e:
        error_msg = f"Unexpected error creating template group: {str(e)}"
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for TemplateGroupMirror (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            raise self.retry(countdown=5, exc=e)
        else:
            celery_logger.error(
                f"TemplateGroupMirror failed after retries: {error_msg}"
            )
            raise ServiceErrorHandler(error_msg)
