from zabbixproxy.tasks.host_creation import host_creation_task
from zabbixproxy.tasks.host_creation.agent_base_host_creation import (
    agent_base_host_creation_task,
)
from zabbixproxy.tasks.host_creation.host_creation_workflow import (
    host_creation_workflow,
)
from zabbixproxy.tasks.host_deletion.host_deletion_workflow import (
    host_deletion_workflow,
)
from zabbixproxy.tasks.host_lifecycle_handlers import (
    update_host_lifecycle_status_failure_task,
    update_host_lifecycle_status_success_task,
)
