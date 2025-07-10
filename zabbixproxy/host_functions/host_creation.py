import logging
import time

import requests

zabbix_logger = logging.getLogger("zabbix")
from utils import ServiceErrorHandler


def host_creation(
    api_url,
    auth_token,
    hostgroup,
    host_name,
    ip,
    port,
    dns,
    useip,
    max_retries=3,
    retry_delay=2,
):
    """
    Create a simple check host in Zabbix.
    This function attempts to create a host in Zabbix with the specified parameters.
    It retries the operation up to `max_retries` times with a delay of `retry_delay` seconds
    between attempts in case of failure.
    it accepts the following parameters:
    - api_url: The URL of the Zabbix API.
    - auth_token: The authentication token for the Zabbix API.
    - hostgroup: The ID of the host group to which the host will be added.
    - host_name: The name of the host to be created.
    - ip: The IP address of the host.
    - port: The port number for the host (default is 10050).
    - dns: The DNS name of the host (optional).
    - useip: Whether to use the IP address (1 for true, 0 for false).
    - max_retries: The maximum number of retry attempts (default is 3).
    - retry_delay: The delay in seconds between retry attempts (default is 2).
    Returns:
        The ID of the created host if successful.
        Raises:
            ServiceErrorHandler: If the host creation fails after all retries.
            requests.RequestException: If there is a network error during the request.
            ValueError: If the response from Zabbix is not valid JSON.
            KeyError: If the expected keys are not present in the response.
            Exception: For any other unexpected errors.
    """
    try:
        for attempt in range(max_retries):
            try:
                zabbix_logger.info(
                    f"Attempting to create host '{host_name}' (attempt {attempt + 1}/{max_retries}) "
                )

                interfaces = [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": useip,
                        "ip": ip,
                        "dns": dns,
                        "port": port,
                    }
                ]

                response = requests.post(
                    f"{api_url}/api_jsonrpc.php",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {auth_token}",
                    },
                    json={
                        "jsonrpc": "2.0",
                        "method": "host.create",
                        "params": {
                            "host": host_name,
                            "interfaces": interfaces,
                            "groups": [{"groupid": hostgroup}],
                        },
                        "id": 1,
                    },
                    timeout=10,
                )

                try:
                    response_data_for_log = response.json()
                except ValueError:
                    zabbix_logger.error("Invalid JSON received from Zabbix.")
                    raise ServiceErrorHandler("Host creation please try again later")

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

                # Success case
                hostid = result["result"]["hostids"][0]
                zabbix_logger.info(
                    f"Host '{host_name}' created successfully with ID: {hostid}"
                )
                return hostid

            except requests.RequestException as e:
                zabbix_logger.error(
                    f"Network error during host creation (attempt {attempt + 1}): {str(e)}"
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
                        "Authentication error during host creation, token may be invalid"
                    )
                    raise
                zabbix_logger.error(
                    f"Zabbix service error (attempt {attempt + 1}): {str(e)}"
                )
            except Exception as e:
                zabbix_logger.error(
                    f"Unexpected error during host creation (attempt {attempt + 1}): {str(e)}"
                )

            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    except Exception as e:
        err_msg = str(e)
        zabbix_logger.critical(
            f"Host creation failed after {max_retries} attempts {err_msg}"
        )
        raise ServiceErrorHandler("Host creation failed please try again later")
