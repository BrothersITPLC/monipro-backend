import logging
import time

import requests

logger = logging.getLogger(__name__)


class ZabbixServiceError(Exception):
    """Exception raised for errors in Zabbix service interactions."""

    pass


def create_host_group(api_url, auth_token, name, max_retries=3, retry_delay=2):
    """
    Create a host group in Zabbix.

    Args:
        api_url: Zabbix API URL
        auth_token: Zabbix authentication token
        name: Name for the host group
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Host group ID string

    Raises:
        ZabbixServiceError: If host group creation fails after max_retries
    """
    for attempt in range(max_retries):
        try:
            logger.info(
                f"Attempting to create host group '{name}' (attempt {attempt + 1}/{max_retries})"
            )

            response = requests.post(
                f"{api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}",
                },
                json={
                    "jsonrpc": "2.0",
                    "method": "hostgroup.create",
                    "params": {"name": name},
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

                # Check if the host group already exists
                if "already exists" in error_message.lower():
                    logger.warning(
                        f"Host group '{name}' already exists, attempting to retrieve its ID"
                    )
                    return get_host_group_id(api_url, auth_token, name)

                raise ZabbixServiceError(f"Host group creation error: {error_message}")

            # Success case
            groupid = result["result"]["groupids"][0]
            logger.info(f"Host group '{name}' created successfully with ID: {groupid}")
            return groupid

        except requests.RequestException as e:
            logger.error(
                f"Network error during host group creation (attempt {attempt + 1}): {str(e)}"
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
                    "Authentication error during host group creation, token may be invalid"
                )
                raise
            logger.error(f"Zabbix service error (attempt {attempt + 1}): {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error during host group creation (attempt {attempt + 1}): {str(e)}"
            )

        # Only sleep if we're going to retry
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    # If we get here, all retries failed
    logger.critical(f"Host group creation failed after {max_retries} attempts")
    raise ZabbixServiceError(f"Host group creation failed after {max_retries} attempts")


def get_host_group_id(api_url, auth_token, name):
    """
    Get the ID of an existing host group by name.

    Args:
        api_url: Zabbix API URL
        auth_token: Zabbix authentication token
        name: Name of the host group to find

    Returns:
        Host group ID string

    Raises:
        ZabbixServiceError: If the host group cannot be found
    """
    try:
        response = requests.post(
            f"{api_url}/api_jsonrpc.php",
            headers={
                "Content-Type": "application/json",
            },
            json={
                "jsonrpc": "2.0",
                "method": "hostgroup.get",
                "params": {"filter": {"name": [name]}},
                "auth": auth_token,
                "id": 1,
            },
            timeout=10,
        )

        response.raise_for_status()
        result = response.json()

        if "error" in result:
            raise ZabbixServiceError(
                f"Error getting host group: {result['error']['data']}"
            )

        if not result["result"]:
            raise ZabbixServiceError(f"Host group '{name}' not found")

        return result["result"][0]["groupid"]

    except Exception as e:
        logger.error(f"Failed to get host group ID: {str(e)}")
        raise ZabbixServiceError(f"Failed to get host group ID: {str(e)}")
