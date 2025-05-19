import logging
import time

import requests

zabbix_logger = logging.getLogger("zabbix")

from utils import ServiceErrorHandler


def create_simple_check_item_for_template(
    api_url,
    auth_token,
    template_id,
    max_retries=3,
    retry_delay=2,
):
    """
    Create a simple check item in Zabbix for a given template.
    Args:
        api_url: Zabbix API URL
        auth_token: Zabbix authentication token
        template_id: ID of the template to which the item will be added
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    Returns:
        list of item IDs created
    Raises:
        ServiceErrorHandler: If the request fails or the item creation fails
    """
    for attempt in range(max_retries):
        try:
            zabbix_logger.info(
                f"Attempting to create simple check item for template ID '{template_id}' (attempt {attempt + 1}/{max_retries})"
            )

            response = requests.post(
                f"{api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}",
                },
                json=build_request_data(template_id),
            )

            try:
                result = response.json()
            except ValueError:
                zabbix_logger.error("Invalid JSON response from Zabbix API")
                raise ServiceErrorHandler("failed to create item")

            if "error" in result:
                zabbix_logger.error(f"Error creating item: {result['error']}")
                raise ServiceErrorHandler("failed to create item")

            if "result" in result:
                item_ids = [item["itemids"][0] for item in result["result"]]
                zabbix_logger.info(
                    f"Simple check items created successfully: {item_ids}"
                )
                return item_ids
            else:
                zabbix_logger.error("Unexpected response format from Zabbix API")
                raise ServiceErrorHandler("failed to create item")

        except requests.RequestException as e:
            zabbix_logger.error(f"Request failed: {e}")
        except ServiceErrorHandler as e:
            zabbix_logger.error(f"Service error: {e}")
        except Exception as e:
            zabbix_logger.error(f"Unexpected error: {e}")
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
    zabbix_logger.error(
        f"Failed to create simple check items for template ID '{template_id}' after {max_retries} attempts"
    )
    raise ServiceErrorHandler("failed to create item")


def build_request_data(template_id):
    """
    Build the request data for creating a simple check item in Zabbix.

    Args:
        template_id: ID of the template to which the item will be added

    Returns:
        Dictionary containing the request data
    """
    return {
        "jsonrpc": "2.0",
        "method": "item.create",
        "params": [
            {
                "name": "ICMP Ping",
                "key_": "icmpping",
                "hostid": template_id,
                "type": 3,
                "value_type": 3,
                "delay": "30s",
            },
            {
                "name": "ICMP Packet Loss",
                "key_": "icmppingloss",
                "hostid": template_id,
                "type": 3,
                "value_type": 0,
                "delay": "30s",
            },
            {
                "name": "ICMP Response Time",
                "key_": "icmppingsec",
                "hostid": template_id,
                "type": 3,
                "value_type": 0,
                "delay": "30s",
            },
            {
                "name": "HTTP Service Check",
                "key_": "net.tcp.service[http]",
                "hostid": template_id,
                "type": 3,
                "value_type": 3,
                "delay": "30s",
            },
            {
                "name": "SSH Service Check",
                "key_": "net.tcp.service[ssh]",
                "hostid": template_id,
                "type": 3,
                "value_type": 3,
                "delay": "30s",
            },
        ],
        "id": 2,
    }
