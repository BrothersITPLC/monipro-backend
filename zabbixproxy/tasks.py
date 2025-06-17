from zabbixproxy.tasks import (
    agent_base_host_creation_task,
    host_creation_task,
    host_creation_workflow,
    interfaceid_retrieval_task,
    item_creation_task,
    update_host_lifecycle_status_failure_task,
    update_host_lifecycle_status_success_task,
)

__all__ = [
    agent_base_host_creation_task,
    host_creation_task,
    host_creation_workflow,
    interfaceid_retrieval_task,
    item_creation_task,
    update_host_lifecycle_status_failure_task,
    update_host_lifecycle_status_success_task,
]
