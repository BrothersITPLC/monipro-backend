# ansibal/views/ansibal_runner.py
import logging
import tempfile

import ansible_runner
from django.conf import settings

from utils import ServiceErrorHandler

ansible_logger = logging.getLogger("ansibal")


def sanitize_error(error):
    sensitive_terms = ["password", "sudo", "ssh"]
    error = str(error)
    for term in sensitive_terms:
        if term in error.lower():
            return "Authentication or privilege error occurred"
    return error.split("\n")[0][:100]


def format_response(runner, target_host):
    tasks = []
    errors = []

    for event in runner.events:
        if event["event"] in ["runner_on_ok", "runner_on_failed"]:
            task = event["event_data"].get("task", "Unknown Task")
            result = event["event_data"]["res"]

            if event["event"] == "runner_on_ok":
                tasks.append(
                    {
                        "task": task,
                        "status": "success",
                        "details": result.get("msg", "Task completed"),
                    }
                )
            else:
                error_msg = sanitize_error(result.get("msg", "Unknown error"))
                errors.append({"task": task, "status": "error", "details": error_msg})

    success = True if len(errors) == 0 else False

    return {
        "host": target_host,
        "overall_success": success,
        "successfully_executed_tasks": tasks,
        "unsuccessfully_executed_tasks": errors,
        "stats": {
            "total_tasks": len(tasks) + len(errors),
            "successful": len(tasks),
            "failed": len(errors),
        },
    }


def create_zabbix_agent(port, target_host, username, hostname, password, tags=None):
    if port is None and password is None and username is None and target_host is None:
        ansible_logger.error(f"Port, password, or username is missing to {hostname}")
        raise ServiceErrorHandler(
            f"Port, password, or username is missing to {hostname}"
        )

    ansible_logger.info(
        f"Creating Zabbix agent on {hostname} with {target_host} and port {port}"
    )
    try:
        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as inv_file:
            inv_content = f"""
            [target]
            {target_host}
            
            [target:vars]
            ansible_user={username}
            ansible_ssh_pass={password}
            ansible_become_pass={password}
            ansible_python_interpreter=/usr/bin/python3
            ansible_ssh_common_args='-o StrictHostKeyChecking=no -o ConnectTimeout=30'
            """
            inv_file.write(inv_content.strip())
            inv_file.flush()

            ansible_logger.info(f"Inventory content:\n{inv_content} ")

            # Create the runner configuration
            runner_config = {
                "playbook": settings.ZABBIX_PLAYBOOK_PATH,
                "inventory": inv_file.name,
                "extravars": {"port": port},
                "quiet": False,
                "json_mode": False,
                "suppress_env_files": True,
            }

            # Add tags if specified
            if tags:
                runner_config["tags"] = tags
                ansible_logger.info(f"Running playbook with tags: {tags}")

            runner = ansible_runner.run(**runner_config)

            ansible_logger.info(f"Ansible run completed with status: {runner.status}")
            ansible_logger.error(f"Ansible events: {runner.events}")
            ansible_logger.error(f"Ansible stdout:\n{runner.stdout.read()}")

            formatted = format_response(runner, target_host)
            return formatted

    except Exception as e:
        ansible_logger.exception(
            f"An error occurred during deployment to {target_host}: {str(e)}"
        )
        raise ServiceErrorHandler("Internal server error")
