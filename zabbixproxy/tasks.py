
# Import all tasks from individual modules
from zabbixproxy.tasks import (
    create_host_workflow,
    create_zabbix_host_record_task,
    create_zabbix_host_task,
    deploy_zabbix_agent_task,
)

# Re-export all tasks
__all__ = [
    'deploy_zabbix_agent_task',
    'create_zabbix_host_task',
    'create_zabbix_host_record_task',
    'create_host_workflow',
]