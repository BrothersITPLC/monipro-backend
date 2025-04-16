import logging
from typing import Any, Dict, Optional, cast

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.models import ZabbixHost, ZabbixHostGroup

django_logger = logging.getLogger("django")

@shared_task(bind=True, max_retries=3)
def create_zabbix_host_record_task(
    self,
    prev_task_result,
):
    """
    Celery task to create a ZabbixHost record in the database
    """
    params = prev_task_result.get("next_task_params", {})
    hostgroup = params.get("hostgroup")
    hostid = params.get("hostid")
    host = params.get("host")
    ip = params.get("ip")
    port = params.get("port")
    dns = params.get("dns")
    host_template = params.get("host_template")
    device_type = params.get("device_type")
    network_device_type = params.get("network_device_type")
    username = params.get("username")
    password = params.get("password")
    network_type = params.get("network_type")

    django_logger.info(f"Creating host record with parameters: hostgroup={hostgroup}, hostid={hostid}, host={host}")

    try:
        try:
            hostgroup_obj = cast(Any,ZabbixHostGroup).objects.get(hostgroupid=hostgroup)
        except cast(Any,ZabbixHostGroup).DoesNotExist:
            raise ServiceErrorHandler(f"Host group with ID {hostgroup} not found")

        zabbix_host = cast(Any, ZabbixHost).objects.create(
            hostgroup=hostgroup_obj,
            hostid=hostid,
            host=host,
            ip=ip,
            port=port,
            dns=dns,
            host_template=host_template,
            device_type=device_type,
            network_device_type=network_device_type,
            username=username,
            password=password,
            network_type=network_type,
        )

        if zabbix_host and zabbix_host.id:
            return {
                "status": "success",
                "message": f"Successfully created Zabbix host record for '{host}'",
            }
        else:
            raise ServiceErrorHandler("Host record was not created properly")

    except ServiceErrorHandler as e:
        error_msg = f"Error creating Zabbix host record: {str(e)}"
        return {"status": "error", "message": f"Error creating Zabbix host record {error_msg}"}

    except Exception as e:
        error_msg = f"Error creating Zabbix host record: {str(e)}"

        if self.request.retries < self.max_retries:
            return self.retry(countdown=5)

        return {"status": "error", "message": f"host record creation failed {error_msg}"}