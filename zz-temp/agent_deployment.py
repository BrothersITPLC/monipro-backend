import logging
import re
from typing import Any, Dict, Optional, cast

from celery import shared_task

from zabbixproxy.ansibal.functions.ansibal_runner import create_zabbix_agent
from zabbixproxy.models import TaskStatus

django_logger = logging.getLogger("django")
ansible_logger = logging.getLogger("zabbix")


@shared_task(bind=True)
def deploy_zabbix_agent_task(
    self,
    port: int,
    target_host: str,
    username: str,
    hostname: str,
    password: str,
    tags: str = "install",
    task_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Celery task to deploy Zabbix agent using Ansible
    """
    # Update task status to in_progress
    if task_id:
        try:
            task_status = cast(Any,TaskStatus).objects.get(task_id=task_id)
            task_status.update_status("in_progress")
        except cast(Any,TaskStatus).DoesNotExist:
            django_logger.error(f"Task with ID {task_id} not found")
            return {"success": "error", "message": "Task not found"}

    try:
        # Call the ansible runner function
        agent_response = create_zabbix_agent(
            port=port,
            target_host=target_host,
            username=username,
            hostname=hostname,
            password=password,
            tags=tags,
        )

        # The response is already a dictionary, not a Response object
        success = agent_response.get("overall_success", False)
        status = "completed" if success else "failed"
        successful_task = agent_response.get("stats", {}).get("successful", 0)
        faild_task = agent_response.get("stats", {}).get("failed", 0)
        error_details = []

        # Get the task lists from the response
        successfully_executed_tasks = agent_response.get("successfully_executed_tasks", [])
        unsuccessfully_executed_tasks = agent_response.get("unsuccessfully_executed_tasks", [])
        
        # Update task status if task_id is provided
        if task_id:
            task_status.status = status
            task_status.successful_task = successful_task
            task_status.faild_task = faild_task
            task_status.successfully_executed_tasks = successfully_executed_tasks
            task_status.unsuccessfully_executed_tasks = unsuccessfully_executed_tasks
            
            # Set error message if there are any failed tasks
            if not success and unsuccessfully_executed_tasks:
                for error in unsuccessfully_executed_tasks:
                    error_details.append(f"{error.get('task', 'Unknown task')}: {error.get('details', 'No details')}")
                task_status.error_message = "Agent deployment failed: " + "; ".join(error_details)
            
            task_status.save()

        if success:
            return {
                "success": "success",
                "message": "Zabbix agent deployed successfully",
            }
        else:
            return {
                "status": "error","message":error_details
            }
    except Exception as e:
        error_msg = f"Error deploying Zabbix agent: {str(e)}"
        if task_id:
            task_status.update_status("failed", error_message=error_msg)
        return {
            "success": "error",
            "message": error_msg,
        }

