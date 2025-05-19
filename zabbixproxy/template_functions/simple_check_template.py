import logging
import time

import requests

zabbix_logger = logging.getLogger("zabbix")

from utils import ServiceErrorHandler


def create_simple_check_template(
    api_url,
    auth_token,
    template_name,
    max_retries=3,
    retry_delay=2,
):
    """
    Create a simple check template in Zabbix.

    Args:
        api_url: Zabbix API URL
        auth_token: Zabbix authentication token
        template_name: Name for the new template
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Template ID string

    Raises:
        ServiceErrorHandler: If the API request fails or the template creation fails.
    """

    for attempt in range(max_retries):
        try:
            zabbix_logger.info(
                f"Attempting to create simple check template '{template_name}' (attempt {attempt + 1}/{max_retries})"
            )

            response = requests.post(
                f"{api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}",
                },
                json=build_request_data(template_name),
            )

            try:
                result = response.json()
            except ValueError:
                zabbix_logger.error("Invalid JSON response from Zabbix API")
                raise ServiceErrorHandler("failed to create template")
            if "error" in result:
                zabbix_logger.error(f"Error creating template: {result['error']}")
                raise ServiceErrorHandler("failed to create template")
            if "result" in result:
                template_id = result["result"]["templateids"][0]
                zabbix_logger.info(
                    f"Simple check template '{template_name}' created successfully with ID: {template_id}"
                )
                return template_id
            else:
                zabbix_logger.error("Unexpected response format from Zabbix API")
                raise ServiceErrorHandler("failed to create template")

        except requests.RequestException as e:
            zabbix_logger.error(f"Error creating template: {e}")
            raise ServiceErrorHandler("failed to create template")

        except ServiceErrorHandler as e:
            zabbix_logger.error(f"Error creating template: {e}")
            raise ServiceErrorHandler("failed to create template")

        except Exception as e:
            zabbix_logger.error(f"Unexpected error: {e}")

        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    zabbix_logger.error("Failed to create template after all retries")
    raise ServiceErrorHandler("failed to create template")


def build_request_data(template_name):
    """Builds the request data for creating a simple check template.
    Args:
        api_url: Zabbix API URL
        auth_token: Zabbix authentication token
        template_name: Name for the new template
    Returns:
        A dictionary containing the request data for creating a simple check template.
    """
    return {
        "jsonrpc": "2.0",
        "method": "template.create",
        "params": {"host": {template_name}},
        "id": 1,
    }
