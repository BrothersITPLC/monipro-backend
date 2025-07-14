import logging

from celery import shared_task

celery_logger = logging.getLogger("celery")
from utils import ServiceErrorHandler
from zabbixproxy.models import TemplateGroupMirror
from zabbixproxy.tasks.template_group_creation.create_template_group import (
    create_zabbix_template_group,
)


@shared_task(bind=True)
def template_group_creation_workflow(
    self,
    api_url,
    auth_token,
    template_group_name,
):
    """
    a function to Orchestrates the entire template group creation workflow and tracks status in the database.
    """

    try:
        template_group_instance = TemplateGroupMirror.objects.filter(
            template_group_id=template_group_name
        ).first()
        if not template_group_instance:
            celery_logger.error(
                f"Template group with Name {template_group_name} does not exist."
            )
            raise ServiceErrorHandler(
                f"Template group with Name {template_group_name} does not exist."
            )

        workflow_chain = create_zabbix_template_group.s(
            api_url=api_url,
            auth_token=auth_token,
            temp_group_name=template_group_name,
        )
        workflow_chain.apply_async()
        celery_logger.info(
            f"Template Group creation workflow initiated for template '{template_group_name}'."
        )
        return {
            "status": "success",
            "message": f"Template Group creation workflow initiated for template '{template_group_name}'.",
        }

    except ServiceErrorHandler as e:
        celery_logger.error(f"Error creating template group: {str(e)}")
        raise ServiceErrorHandler(f"Error creating template group: {str(e)}")
    except Exception as e:
        celery_logger.error(
            f"Unexpected error in template group creation workflow: {str(e)}"
        )
        raise ServiceErrorHandler(
            f"Unexpected error in template group creation workflow: {str(e)}"
        )
