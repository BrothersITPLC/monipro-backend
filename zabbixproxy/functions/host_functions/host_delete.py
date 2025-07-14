import logging
import time

import requests

from utils import ServiceErrorHandler

zabbix_logger = logging.getLogger("zabbix")


def delete_host(api_url, auth_token, host_id, max_retries=3, retry_delay=2):
    """
    Delete a Zabbix host by host_id.
    Returns True if deletion is successful, otherwise raises ServiceErrorHandler.
    """
    if not api_url or not auth_token or not host_id:
        raise ValueError("API URL, auth token, and host ID are required")

    for attempt in range(1, max_retries + 1):
        try:
            zabbix_logger.info(
                f"Attempting to delete host ID '{host_id}' (attempt {attempt}/{max_retries})"
            )

            response = requests.post(
                f"{api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}",
                },
                json={
                    "jsonrpc": "2.0",
                    "method": "host.delete",
                    "params": [str(host_id)],
                    "id": 1,
                },
                timeout=10,
            )

            try:
                response_data = response.json()
            except ValueError:
                raise ServiceErrorHandler(
                    "Invalid JSON received from Zabbix during deletion"
                )

            if "error" in response_data:
                error = response_data["error"]
                zabbix_logger.error(
                    f"Zabbix API Error [{error.get('code', 'N/A')}]: "
                    f"{error.get('message', '')} - {error.get('data', '')}"
                )
                raise ServiceErrorHandler(
                    "Zabbix API returned an error during host deletion"
                )

            result = response_data.get("result", {})
            deleted_ids = result.get("hostids", [])

            if str(host_id) in deleted_ids:
                zabbix_logger.info(f"Host ID '{host_id}' deleted successfully")
                return True

            zabbix_logger.warning(f"Host ID '{host_id}' not found in deletion response")
            return False

        except requests.RequestException as e:
            zabbix_logger.warning(
                f"Request error during deletion attempt {attempt}: {e}"
            )
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                raise ServiceErrorHandler("Failed to delete host after retries")

        except ServiceErrorHandler:
            raise

        except Exception as e:
            zabbix_logger.exception("Unexpected error during host deletion")
            raise ServiceErrorHandler("Unexpected error during host deletion")

    return False
