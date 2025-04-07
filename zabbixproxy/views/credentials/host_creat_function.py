import logging
import time

import requests

logger = logging.getLogger(__name__)


class ZabbixServiceError(Exception):
    """Exception raised for errors in Zabbix service interactions."""

    pass


def create_host(
    api_url,
    auth_token,
    hostgroup,
    host,
    ip,
    port,
    dns,
    host_template,
    max_retries=3,
    retry_delay=2,
):
    """
    Create a host in Zabbix.

    Args:
        api_url: Zabbix API URL
        auth_token: Zabbix authentication token
        hostgroup: Host group ID to assign the host to
        host: Name for the new host
        ip: IP address of the host
        port: Port number for the host
        dns: DNS name for the host
        host_template: Template ID to assign to the host
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Host ID string

    Raises:
        ZabbixServiceError: If host creation fails after max_retries
    """
    for attempt in range(max_retries):
        try:
            logger.info(
                f"Attempting to create host '{host}' (attempt {attempt + 1}/{max_retries})"
            )

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
                        "host": host,
                        "interfaces": [
                            {
                                "type": 1,
                                "main": 1,
                                "useip": 1,
                                "ip": ip,
                                "dns": dns,
                                "port": port,
                            }
                        ],
                        "groups": [{"groupid": hostgroup}],
                        "templates": [{"templateid": host_template}],
                    },
                    "id": 1,
                },
                timeout=10,
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

                # Check if the host already exists
                if "already exists" in error_message.lower():
                    logger.warning(f"Host '{host}' already exists")
                    raise ZabbixServiceError(f"Host '{host}' already exists")

                raise ZabbixServiceError(f"Host creation error: {error_message}")

            # Success case
            hostid = result["result"]["hostids"][0]
            logger.info(f"Host '{host}' created successfully with ID: {hostid}")
            return hostid

        except requests.RequestException as e:
            logger.error(
                f"Network error during host creation (attempt {attempt + 1}): {str(e)}"
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
                    "Authentication error during host creation, token may be invalid"
                )
                raise
            logger.error(f"Zabbix service error (attempt {attempt + 1}): {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error during host creation (attempt {attempt + 1}): {str(e)}"
            )

        # Only sleep if we're going to retry
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    # If we get here, all retries failed
    logger.critical(f"Host creation failed after {max_retries} attempts")
    raise ZabbixServiceError(f"Host creation failed after {max_retries} attempts")
