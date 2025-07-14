import logging

from celery import shared_task

celery_logger = logging.getLogger("celery")
from utils import ServiceErrorHandler
from zabbixproxy.models import TemplateGroupMirror, TemplateMirror
from zabbixproxy.tasks.template_creation.create_template import create_zabbix_template


@shared_task(bind=True)
def template_creation_workflow(
    self,
    api_url,
    auth_token,
    template_group_id,
    template_name,
):
    """
    a function to Orchestrates the entire template creation workflow and tracks status in the database.
    """

    try:
        template_group_instance = TemplateGroupMirror.objects.filter(
            template_group_id=template_group_id
        ).first()
        if not template_group_instance:
            celery_logger.error(
                f"Template group with ID {template_group_id} does not exist."
            )
            raise ServiceErrorHandler(
                f"Template group with ID {template_group_id} does not exist."
            )

        template_instance = TemplateMirror.objects.filter(
            template_name=template_name
        ).first()
        if template_instance:
            celery_logger.error(f"Template with name {template_name} already exists.")
            raise ServiceErrorHandler(
                f"Template with name {template_name} already exists."
            )

        workflow_chain = create_zabbix_template.s(
            api_url=api_url,
            auth_token=auth_token,
            temp_name=template_name,
            temp_group_id=template_group_id,
        )
        workflow_chain.apply_async()
        celery_logger.info(
            f"Template creation workflow initiated for template '{template_name}' in group '{template_group_id}'."
        )
        return {
            "status": "success",
            "message": f"Template creation workflow initiated for template '{template_name}' in group '{template_group_id}'.",
        }

    except ServiceErrorHandler as e:
        celery_logger.error(f"Error creating template: {str(e)}")
        raise ServiceErrorHandler(f"Error creating template: {str(e)}")
    except Exception as e:
        celery_logger.error(f"Unexpected error in template creation workflow: {str(e)}")
        raise ServiceErrorHandler(
            f"Unexpected error in template creation workflow: {str(e)}"
        )
