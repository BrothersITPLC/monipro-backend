import logging
import uuid
from typing import Any, Dict, cast

from celery import shared_task
from django.contrib.auth import get_user_model

from zabbixproxy.models import TaskStatus
from zabbixproxy.tasks.agent_deployment import deploy_zabbix_agent_task
from zabbixproxy.tasks.host_creation import create_zabbix_host_task
from zabbixproxy.tasks.host_record import create_zabbix_host_record_task

zabbix_logger = logging.getLogger("zabbix")
django_logger = logging.getLogger("django")
ansibal_logger = logging.getLogger("ansible")

User = get_user_model()

@shared_task(bind=True)
def create_host_workflow(
    self,
    user_id: int,
    host: str,
    ip: str,
    port: int,
    username: str,
    password: str,
    dns: str,
    useip: int,
    host_template: int,
    hostgroup: str,
    api_url: str,
    auth_token: str,
    device_type: str,
    network_device_type: str,
    network_type: str,
    tags: str = "install",
) -> Dict[str, Any]:
    """
    Orchestrates the entire host creation workflow and tracks status in the database
    """
    # Create main task record
    agent_task_id = uuid.uuid4()
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

        agent_task = deploy_zabbix_agent_task.apply_async(
            kwargs={
                "port": port,
                "target_host": ip,
                "username": username,
                "hostname": host,
                "password": password,
                "tags": tags,
                "task_id": str(parent_task.task_id),  # Use task_id field instead of id
            }
        )

        # Wait for agent deployment to complete
        agent_result = agent_task.get()
        if agent_result.get("status") == "success":
            message = agent_result.get("message", "")
            ansibal_logger.info(message)
            try:
                child_task_id = uuid.uuid4()
                child_task = cast(Any, TaskStatus).objects.create(
                    task_id=child_task_id,
                    task_type="zabbix_host_creation",
                    status="pending",
                    parent_task=parent_task,
                    user=user,
                    host_ip=ip,
                    dns=dns,
                )
                
                host_task = create_zabbix_host_task.apply_async(
                    kwargs={
                        "api_url": api_url,
                        "auth_token": auth_token,
                        "hostgroup": hostgroup,
                        "host": host,
                        "ip": ip,
                        "port": port,
                        "dns": dns,
                        "useip": useip,
                        "host_template": host_template,
                        "task_id": str(child_task.id),
                    }
                )

                # Wait for host creation to complete
                host_result = host_task.get()
                if host_result.get("status") == "success":
                    message = host_result.get("message", "")
                    zabbix_logger.info(message)
                    try:
                        # 3. Create host record in database
                        record_task = create_zabbix_host_record_task.apply_async(
                            kwargs={
                                "hostgroup": hostgroup,
                                "hostid": host_result.get("hostid"),
                                "host": host,
                                "ip": ip,
                                "port": port,
                                "dns": dns,
                                "host_template": host_template,
                                "device_type": device_type,
                                "network_device_type": network_device_type,
                                "username": username,
                                "password": password,
                                "network_type": network_type,
                            }
                        )
                        
                        record_result = record_task.get()
                        message = record_result.get("message", "")
                        django_logger.info(message)
                        
                        if record_result.get("status") == "success":
                            return {
                                "status": "success",
                                "message": "Host workflow completed successfully"
                            }
                        else:
                            return {
                                "status": "error",
                                "message": f"Host record creation failed: {message}"
                            }
                    except Exception as e:
                        error_msg = f"Error creating host record: {str(e)}"
                        django_logger.exception(error_msg)
                        return {"status": "error", "message": error_msg}
                else:
                    message = host_result.get("message", "Host creation failed")
                    zabbix_logger.error(message)
                    return {"status": "error", "message": message}
            except Exception as e:
                error_msg = f"Error creating host: {str(e)}"
                zabbix_logger.exception(error_msg)
                return {"status": "error", "message": error_msg}
        else:
            message = agent_result.get("message", "Agent deployment failed")
            ansibal_logger.error(message)
            return {"status": "error", "message": message}
                    
    except Exception as e:
        error_msg = f"Error in host workflow: {str(e)}"
        ansibal_logger.exception(error_msg)
        return {"status": "error", "message": error_msg}
