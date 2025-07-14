import logging
import time

import requests

zabbix_logger = logging.getLogger("zabbix")
from utils import ServiceErrorHandler


def creat_template(
    api_url,
    auth_token,
    temp_name,
    temp_group_id,
    max_retries=3,
    retry_delay=2,
):
    """
    creating a template for monipro and zabbix mirroring
    Args:
        api_url: Zabbix API URL
        auth_token: Zabbix authentication token
        temp_name: A discription for the template
        temp_group_id: A template group id that the template going to belong to
    Returns:
        Template id
    """
    for attempt in range(max_retries):
        try:

            zabbix_logger.info(
                f"Attempting to creat template on Template group '{temp_group_id}' with a name '{temp_name}' (attempt {attempt + 1}/{max_retries})"
            )
            params = {"host": {temp_name}, "groups": {"groupid": {temp_group_id}}}
            response = requests.post(
                f"{api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}",
                },
                json={
                    "jsonrpc": "2.0",
                    "method": "template.create",
                    "params": params,
                    "id": 1,
                },
            )
            try:
                response_data_for_log = response.json()
            except ValueError:
                zabbix_logger.error(
                    "Invalid JSON received from Zabbix. While creating a Template"
                )
                raise ServiceErrorHandler(
                    "Template creation Failed please try again later"
                )

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
            template_id = result["result"]["templateids"][0]
            zabbix_logger.info(
                f"Template '{temp_name}' created successfully with ID: {template_id}"
            )
            return template_id
        except requests.RequestException as e:
            zabbix_logger.error(
                f"Network error during template creation (attempt {attempt + 1}): {str(e)}"
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
                    "Authentication error during template creation, token may be invalid"
                )
                raise
            zabbix_logger.error(
                f"Zabbix service error (attempt {attempt + 1}): {str(e)}"
            )
        except Exception as e:
            zabbix_logger.error(
                f"Unexpected error occured during host creation (attempt {attempt + 1}): {str(e)}"
            )

        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    zabbix_logger.critical(f"Template creation failed")
    raise ServiceErrorHandler("Template creation failed please try again later")
