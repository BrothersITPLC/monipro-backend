import logging
import time

import requests

zabbix_logger = logging.getLogger("zabbix")
from utils import ServiceErrorHandler


def get_interfaceid(
    api_url,
    auth_token,
    zabbix_host_hostid,
    host_name,
    max_retries=3,
    retry_delay=2,
):
    """
    Get the interfaceid for a given host name from Zabbix.
    this function accept the follwing parameters:
    - api_url: the URL of the Zabbix API endpoint
    - auth_token: the authentication token for the Zabbix API
    - hostids: the zabbix_host_hostid of the hosts to search for
    - host_name: the name of the host to search for
    - max_retries: the maximum number of retries to attempt
    - retry_delay: the delay between retries in seconds
    """
    for attempt in range(max_retries):
        try:
            zabbix_logger.info(
                f"Attempting to get interfaceid for host '{host_name} ' (attempt {attempt + 1}/{max_retries})"
            )

            response = requests.post(
                f"{api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}",
                },
                json={
                    "jsonrpc": "2.0",
                    "method": "hostinterface.get",
                    "params": {
                        "output": ["interfaceid"],
                        "hostids": f"{zabbix_host_hostid}",
                    },
                    "id": 1,
                },
                timeout=10,
            )

            try:
                response_data_for_log = response.json()
            except ValueError as e:
                er_mess = str(e)
                zabbix_logger.error("Invalid JSON received from Zabbix.")
                raise ServiceErrorHandler(
                    f"Host creation please try again later,{er_mess}"
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

            # Success case
            result = response.json()
            interfaces = result["result"]
            if not interfaces:
                raise ServiceErrorHandler(f"No interfaces found for host '{host_name}'")
            interfaceid = interfaces[0]["interfaceid"]
            zabbix_logger.info(f"Interfaceid for host '{host_name}' is {interfaceid}")
            return interfaceid

        except requests.RequestException as e:
            zabbix_logger.error(
                f"Network error during interfaceid retrieval (attempt {attempt + 1}): {str(e)}"
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
                    "Authentication error during interfaceid retrieval, token may be invalid"
                )
                raise
            zabbix_logger.error(
                f"Zabbix service error (attempt {attempt + 1}): {str(e)}"
            )
        except Exception as e:
            zabbix_logger.error(
                f"Unexpected error during interfaceid retrieval (attempt {attempt + 1}): {str(e)}"
            )

        # Only sleep if we're going to retry
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    # If we get here, all retries failed
    zabbix_logger.critical(f"interfaceid retrieval failed after {max_retries} attempts")
    raise ServiceErrorHandler(
        "interfaceid retrieval failed please try again later maximum retries"
    )
