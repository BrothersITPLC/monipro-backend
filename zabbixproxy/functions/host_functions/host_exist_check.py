import logging
import time

import requests

from utils import ServiceErrorHandler

zabbix_logger = logging.getLogger("zabbix")


def check_host_exist(
    api_url, auth_token, host_id, host_name, max_retries=3, retry_delay=2
):
    """
    Check if a host exists in Zabbix using either host_id or host_name.
    Returns True if the host exists, False otherwise.
    Raises ServiceErrorHandler on failure.
    """

    if not api_url or not auth_token:
        raise ValueError("API URL and auth token are required")

    if not host_id and not host_name:
        raise ValueError("Either host_id or host_name must be provided")

    # Build Zabbix API request params
    params = {"output": ["hostid", "host", "name"]}
    if host_name:
        params["filter"] = {"host": [host_name]}
    elif host_id:
        params["hostids"] = [str(host_id)]

    for attempt in range(1, max_retries + 1):
        try:
            zabbix_logger.info(
                f"Checking host existence (attempt {attempt}/{max_retries})"
            )

            response = requests.post(
                f"{api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}",
                },
                json={
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": params,
                    "id": 1,
                },
                timeout=10,
            )

            try:
                response_data = response.json()
            except ValueError:
                raise ServiceErrorHandler("Invalid JSON received from Zabbix API")

            if "error" in response_data:
                error = response_data["error"]
                zabbix_logger.error(
                    f"Zabbix API Error [{error.get('code', 'N/A')}]: "
                    f"{error.get('message', '')} - {error.get('data', '')}"
                )
                raise ServiceErrorHandler("Zabbix API returned an error")

            result = response_data.get("result", [])
            if not result:
                zabbix_logger.info("Host not found in Zabbix")
                return False

            if host_id:
                for item in result:
                    if str(item["hostid"]) == str(host_id):
                        zabbix_logger.info(f"Host with ID '{host_id}' exists")
                        return True
                zabbix_logger.info(f"Host ID '{host_id}' not matched in result")
                return False

            zabbix_logger.info(f"Host with name '{host_name}' exists")
            return True

        except requests.RequestException as e:
            zabbix_logger.warning(f"Request error during attempt {attempt}: {e}")
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                raise ServiceErrorHandler(
                    "Failed to check host existence after retries"
                )

        except ServiceErrorHandler:
            raise

        except Exception as e:
            zabbix_logger.exception("Unexpected error during host existence check")
            raise ServiceErrorHandler("Unexpected error during host existence check")

    return False  # Defensive fallback
