import logging
import time

import requests

logger = logging.getLogger(__name__)


class ZabbixServiceError(Exception):
    """Exception raised for errors in Zabbix service interactions."""

    pass


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
        ZabbixServiceError: If user group creation fails after max_retries
    """
    for attempt in range(max_retries):
        try:
            logger.info(
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

            # Check HTTP errors
            if response.status_code != 200:
                logger.error(f"HTTP error: {response.status_code}")
                raise ZabbixServiceError(f"HTTP error: {response.status_code}")

            result = response.json()

            # Check for API errors
            if "error" in result:
                error_message = result["error"].get(
                    "data", result["error"].get("message", "Unknown error")
                )
                logger.error(f"Zabbix API error: {error_message}")

                # Check if the user group already exists
                if "already exists" in error_message.lower():
                    logger.warning(
                        f"User group '{name}' already exists, attempting to retrieve its ID"
                    )
                    # You could add a get_user_group_id function here similar to host_group.py
                    raise ZabbixServiceError(f"User group '{name}' already exists")

                raise ZabbixServiceError(f"User group creation error: {error_message}")

            # Success case
            usergroupid = result["result"]["usrgrpids"][0]
            logger.info(
                f"User group '{name}' created successfully with ID: {usergroupid}"
            )
            return usergroupid

        except requests.RequestException as e:
            logger.error(
                f"Network error during user group creation (attempt {attempt + 1}): {str(e)}"
            )
        except (ValueError, KeyError) as e:
            logger.error(
                f"Invalid response from Zabbix API (attempt {attempt + 1}): {str(e)}"
            )
        except ZabbixServiceError as e:
            # Don't retry if the error is due to invalid auth token
            if (
                "not authorized" in str(e).lower()
                or "session terminated" in str(e).lower()
            ):
                logger.critical(
                    "Authentication error during user group creation, token may be invalid"
                )
                raise
            logger.error(f"Zabbix service error (attempt {attempt + 1}): {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error during user group creation (attempt {attempt + 1}): {str(e)}"
            )

        # Only sleep if we're going to retry
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    # If we get here, all retries failed
    logger.critical(f"User group creation failed after {max_retries} attempts")
    raise ZabbixServiceError(f"User group creation failed after {max_retries} attempts")
