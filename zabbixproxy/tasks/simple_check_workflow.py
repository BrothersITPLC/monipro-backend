import logging
import uuid
from typing import Any, Dict, cast

from celery import chain, shared_task
from django.contrib.auth import get_user_model
from django.db import transaction

from zabbixproxy.models import TaskStatus
from zabbixproxy.tasks.agent_deployment import deploy_zabbix_agent_task
from zabbixproxy.tasks.host_creation import create_zabbix_host_task
from zabbixproxy.tasks.host_record import create_zabbix_host_record_task

zabbix_logger = logging.getLogger("zabbix")
django_logger = logging.getLogger("django")
ansibal_logger = logging.getLogger("ansible")

User = get_user_model()


@shared_task(bind=True)
def simple_check_host_create_workflow(
    self,
    user_id: int,
    host: str,
    ip: str,
    port: int,
    dns: str,
    useip: int,
    hostgroup: str,
    api_url: str,
    auth_token: str,
    item_list: str,
    tags: str = "install",
) -> Dict[str, Any]:
    """
    Orchestrates the entire host creation workflow and tracks status in the database
    """
    agent_task_id = str(uuid.uuid4())
    user = User.objects.get(id=user_id)

    try:
        parent_task = cast(Any, TaskStatus).objects.create(
            task_id=agent_task_id,
            task_type="zabbix_agent_creation",
            status="pending",
            user=user,
            host_ip=ip,
            dns=dns,
        )

        host_task_id = str(uuid.uuid4())
        host_task_status = cast(Any, TaskStatus).objects.create(
            task_id=host_task_id,
            task_type="zabbix_host_creation",
            status="pending",
            parent_task=parent_task,
            user=user,
            host_ip=ip,
            dns=dns,
        )

        record_task_id = str(uuid.uuid4())
        record_task_status = cast(Any, TaskStatus).objects.create(
            task_id=record_task_id,
            task_type="zabbix_host_record_creation",
            status="pending",
            parent_task=parent_task,
            user=user,
            host_ip=ip,
            dns=dns,
        )

        def on_transaction_commit():

            chain(
                deploy_zabbix_agent_task.s(
                    port=port,
                    target_host=ip,
                    hostname=host,
                    tags=tags,
                    task_id=str(parent_task.task_id),
                    next_task_params={
                        "api_url": api_url,
                        "auth_token": auth_token,
                        "hostgroup": hostgroup,
                        "host": host,
                        "ip": ip,
                        "port": port,
                        "dns": dns,
                        "useip": useip,
                        "record_task_id": record_task_id,
                        "task_id": host_task_id,
                    },
                ),
                create_zabbix_host_task.s(),
                create_zabbix_host_record_task.s(),
            ).apply_async()

        transaction.on_commit(on_transaction_commit)

        return {
            "status": "success",
            "message": "Host creation workflow started",
            "task_id": agent_task_id,
        }

    except Exception as e:
        error_msg = f"Error in host workflow: {str(e)}"
        ansibal_logger.exception(error_msg)
        return {"status": "error", "message": error_msg}
