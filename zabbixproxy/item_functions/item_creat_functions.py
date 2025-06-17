import logging
import time

import requests

from item_types.models import MonitoringCategoryAndItemType

zabbix_logger = logging.getLogger("zabbix")
from utils import ServiceErrorHandler


def item_create_function(
    api_url,
    auth_token,
    host_name,
    zabbix_host_hostid,
    item_template_list,
    interface_id,
    max_retries=3,
    retry_delay=2,
):
    """
    This function is used to create item in zabbix fro a specific host

    """
    for attempt in range(max_retries):
        try:
            category_id = item_template_list.get("category_id")
            template_ids = item_template_list.get("template")

            try:
                monitor_category_and_item_type = (
                    MonitoringCategoryAndItemType.objects.get(id=category_id)
                )
            except MonitoringCategoryAndItemType.DoesNotExist:
                zabbix_logger.error(
                    f"MonitoringCategoryAndItemType not found for category_id={category_id}"
                )
                raise ServiceErrorHandler(
                    f"Configuration error: MonitoringCategoryAndItemType not found for category_id={category_id}"
                )

            item_list = []
            local_templates = monitor_category_and_item_type.template

            for template_dict in local_templates:
                if template_dict.get("template_id") in template_ids:
                    item_types = template_dict.get("item_types", [])
                    item_list.extend(item_types)

            for item in item_list:
                item["interfaceid"] = interface_id
                item["hostid"] = zabbix_host_hostid
                item["history"] = "14d"

                if item["value_type"] in [0, 3]:
                    item["trends"] = "365d"
                else:
                    item["trends"] = "0"

            zabbix_logger.info(
                f"Attempting create item for host '{host_name}' (attempt {attempt + 1}/{max_retries})"
            )

            response = requests.post(
                f"{api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}",
                },
                json={
                    "jsonrpc": "2.0",
                    "method": "item.create",
                    "params": item_list,
                    "id": 1,
                },
                timeout=10,
            )

            try:
                response_data_for_log = response.json()
            except ValueError:
                zabbix_logger.error("Invalid JSON received from Zabbix.")
                raise ServiceErrorHandler("item create function failed")

            if "error" in response_data_for_log:
                error_info = response_data_for_log["error"]
                error_code = error_info.get("code", "N/A")
                error_message = error_info.get("message", "No message")
                error_data = error_info.get("data", "")

                zabbix_logger.error(
                    f"Zabbix API Error [{error_code}]: {error_message} - {error_data}"
                )

                raise ServiceErrorHandler(f"{error_message}: {error_data}")

            result = response.json()

            item_ids = result["result"].get("itemids")
            if not item_ids:
                zabbix_logger.error(
                    f"Zabbix API response did not contain itemids for host {host_name}."
                )
                raise ServiceErrorHandler("Item creation failed: No item IDs returned.")
            return item_ids

        except requests.RequestException as e:
            zabbix_logger.error(
                f"Network error during item (attempt {attempt + 1}): {str(e)}"
            )
        except (ValueError, KeyError) as e:
            zabbix_logger.error(
                f"Invalid response from Zabbix API (attempt {attempt + 1}): {str(e)}"
            )
        except ServiceErrorHandler as e:
            if (
                "not authorized" in str(e).lower()
                or "session terminated" in str(e).lower()
            ):
                zabbix_logger.critical(
                    "Authentication error during item creation, token may be invalid"
                )
                raise
            zabbix_logger.error(
                f"Zabbix service error (attempt {attempt + 1}): {str(e)}"
            )
        except Exception as e:
            zabbix_logger.error(
                f"Unexpected error during item creation (attempt {attempt + 1}): {str(e)}"
            )

        # Only sleep if we're going to retry
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    # If we get here, all retries failed
    zabbix_logger.critical(f"item creation failed after {max_retries} attempts")
    raise ServiceErrorHandler("item creation failed please try again later")
