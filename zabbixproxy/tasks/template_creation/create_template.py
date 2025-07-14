import logging

from celery import shared_task

celery_logger = logging.getLogger("celery")
from utils import ServiceErrorHandler
from zabbixproxy.functions.template_functions import creat_template
from zabbixproxy.models import TemplateMirror


@shared_task(bind=True, max_retries=3)
def create_zabbix_template(
    self,
    api_url,
    auth_token,
    temp_name,
    temp_group_id,
):
    """
    Celery task to create a Zabbix template.
    """
    if not api_url or not auth_token or not temp_name or not temp_group_id:
        celery_logger.error("missing required parameters for template creation")
        raise ServiceErrorHandler("Missing required parameters for template creation")
    try:
        template_id = creat_template(
            api_url=api_url,
            auth_token=auth_token,
            temp_name=temp_name,
            temp_group_id=temp_group_id,
        )

        if template_id:
            try:
                template_instance = TemplateMirror.objects.get(
                    template_name=temp_name
                ).first()
                template_instance.template_id = template_id
                template_instance.save()
                return {
                    "status": "success",
                    "message": f"Successfully created Zabbix template '{temp_name}' with ID: {template_id}",
                }
            except TemplateMirror.DoesNotExist:
                celery_logger.error(
                    f"Template with this name {temp_name} not found in the database"
                )
                raise ServiceErrorHandler(
                    f"Template with this name {temp_name} not found in the database"
                )

    except ServiceErrorHandler as e:
        error_msg = f"Error creating Zabbix Template: {str(e)}"
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for TemplateMirror (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            raise self.retry(countdown=5, exc=e)
        else:
            celery_logger.error(f"TemplateMirror failed after retries: {error_msg}")
            raise ServiceErrorHandler(error_msg)

    except Exception as e:
        error_msg = f"Unexpected error creating template: {str(e)}"
        if self.request.retries < self.max_retries and (
            "not authorized" in str(e).lower() or "session terminated" in str(e).lower()
        ):
            celery_logger.warning(
                f"Retrying task {self.request.id} for TemplateMirror (attempt {self.request.retries + 1}/{self.max_retries}): {error_msg}"
            )
            raise self.retry(countdown=5, exc=e)
        else:
            celery_logger.error(f"TemplateMirror failed after retries: {error_msg}")
            raise ServiceErrorHandler(error_msg)
