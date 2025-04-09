import logging
import time

import requests

zabbix_logger = logging.getLogger("zabbix")
django_logger = logging.getLogger("django")

from utils import ServiceErrorHandler


def create_user_group(
    api_url, auth_token, name, hostgroup_id, permission=3, max_retries=3, retry_delay=2
):
    """
    Create a user group in Zabbix with specified permissions for a host group.

    Args:
        api_url: Zabbix API URL
        auth_token: Zabbix authentication token
        name: Name for the user group
        hostgroup_id: ID of the host group to assign permissions for
        permission: Permission level (default: 3 for read-write)
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        User group ID string

    Raises:
        ServiceErrorHandler: If user group creation fails after max_retries
    """
    for attempt in range(max_retries):
        try:
            zabbix_logger.info(
                f"Attempting to create user group '{name}' (attempt {attempt + 1}/{max_retries})"
            )

            response = requests.post(
                f"{api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}",
                },
                json={
                    "jsonrpc": "2.0",
                    "method": "usergroup.create",
                    "params": {
                        "name": name,
                        "hostgroup_rights": [
                            {
                                "id": hostgroup_id,
                                "permission": permission,
                            }
                        ],
                    },
                    "id": 1,
                },
                timeout=10,  # Add timeout to prevent hanging requests
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
            
            usergroupid = result["result"]["usrgrpids"][0]
            zabbix_logger.info(
                f"User group '{name}' created successfully with ID: {usergroupid}"
            )
            return usergroupid

        except requests.RequestException as e:
            zabbix_logger.error(
                f"Network error during user group creation (attempt {attempt + 1}): {str(e)}"
            )
        except (ValueError, KeyError) as e:
            zabbix_logger.error(
                f"Invalid response from Zabbix API (attempt {attempt + 1}): {str(e)}"
            )
        except ServiceErrorHandler as e:
            # Don't retry if the error is due to invalid auth token
            if (
                "not authorized" in str(e).lower()
                or "session terminated" in str(e).lower()
            ):
                zabbix_logger.critical(
                    "Authentication error during user group creation, token may be invalid"
                )
                raise
            zabbix_logger.error(f"Zabbix service error (attempt {attempt + 1}): {str(e)}")
        except Exception as e:
            zabbix_logger.error(
                f"Unexpected error during user group creation (attempt {attempt + 1}): {str(e)}"
            )

        # Only sleep if we're going to retry
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    # If we get here, all retries failed
    zabbix_logger.critical(f"User group creation failed after {max_retries} attempts")
    raise ServiceErrorHandler(f"User group creation failed after {max_retries} attempts")
