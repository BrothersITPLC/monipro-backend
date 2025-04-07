import logging
import time

import requests

logger = logging.getLogger(__name__)


class ZabbixServiceError(Exception):
    """Exception raised for errors in Zabbix service interactions."""

    pass


def zabbix_login(api_url, username, password, max_retries=3, retry_delay=2):
    """
    Authenticate with Zabbix API and return auth token.

    Args:
        api_url: Zabbix API URL
        username: Zabbix username
        password: Zabbix password
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Authentication token string

    Raises:
        ZabbixServiceError: If authentication fails after max_retries
    """
    for attempt in range(max_retries):
        try:
            logger.info(
                f"Attempting Zabbix login (attempt {attempt + 1}/{max_retries})"
            )

            response = requests.post(
                f"{api_url}/api_jsonrpc.php",
                json={
                    "jsonrpc": "2.0",
                    "method": "user.login",
                    "params": {
                        "username": username,
                        "password": password,
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
                raise ZabbixServiceError(f"Auth error: {error_message}")

            # Success case
            auth_token = result["result"]
            logger.info("Zabbix authentication successful")
            return auth_token

        except requests.RequestException as e:
            logger.error(
                f"Network error during Zabbix authentication (attempt {attempt + 1}): {str(e)}"
            )
        except (ValueError, KeyError) as e:
            logger.error(
                f"Invalid response from Zabbix API (attempt {attempt + 1}): {str(e)}"
            )
        except ZabbixServiceError as e:
            logger.error(f"Zabbix service error (attempt {attempt + 1}): {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error during Zabbix authentication (attempt {attempt + 1}): {str(e)}"
            )

        # Only sleep if we're going to retry
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    # If we get here, all retries failed
    logger.critical(f"Zabbix authentication failed after {max_retries} attempts")
    raise ZabbixServiceError(
        f"Zabbix authentication failed after {max_retries} attempts"
    )
