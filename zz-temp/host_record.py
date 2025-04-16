import logging
from typing import Any, Dict, Optional, cast

from celery import shared_task

from utils import ServiceErrorHandler
from zabbixproxy.models import ZabbixHost, ZabbixHostGroup


@shared_task(bind=True, max_retries=3)
def create_zabbix_host_record_task(
    self,
    hostgroup: int,
    hostid: str,
    host: str,
    ip: str,
    port: int,
    dns: str,
    host_template: int,
    device_type: str,
    network_device_type: str,
    username: str,
    password: str,
    network_type: str,
) -> Dict[str, Any]:
    """
    Celery task to create a ZabbixHost record in the database
    """

    try:
        try:
            hostgroup_obj = cast(Any,ZabbixHostGroup).objects.get(id=hostgroup)
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

        # Verify the object was created by checking its ID
        if zabbix_host and zabbix_host.id:
            return {
                "status": "success",
                "message": f"Successfully created Zabbix host record for '{host}'",
            }
        else:
            # This should rarely happen, but just in case
            raise ServiceErrorHandler("Host record was not created properly")

    except ServiceErrorHandler as e:
        error_msg = f"Error creating Zabbix host record: {str(e)}"
        return {"status": "error", "message": f"Error creating Zabbix host record {error_msg}"}

    except Exception as e:
        error_msg = f"Error creating Zabbix host record: {str(e)}"

        if self.request.retries < self.max_retries:
            return self.retry(countdown=5)

        return {"status": "error", "message": f"host record creation failed {error_msg}"}