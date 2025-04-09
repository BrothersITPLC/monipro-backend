import logging
import time

import requests

zabbix_logger = logging.getLogger("zabbix")
django_logger = logging.getLogger("django")

from utils import ServiceErrorHandler


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
        ServiceErrorHandler: If authentication fails after max_retries
    """
    for attempt in range(max_retries):
        try:
            zabbix_logger.info(
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
                timeout=10, 
            )

            # Check HTTP errors
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

                raise ServiceErrorHandler("something went wrong please try again later")

            result = response.json()

            # Success case
            auth_token = result["result"]
            zabbix_logger.info("Zabbix authentication successful {auth_token}")
            return auth_token

        except requests.RequestException as e:
            zabbix_logger.error(
                f"Network error during Zabbix authentication (attempt {attempt + 1}): {str(e)}"
            )
        except (ValueError, KeyError) as e:
            zabbix_logger.error(
                f"Invalid response from Zabbix API (attempt {attempt + 1}): {str(e)}"
            )
        except ServiceErrorHandler as e:
            zabbix_logger.error(f"Zabbix service error (attempt {attempt + 1}): {str(e)}")
        except Exception as e:
            zabbix_logger.error(
                f"Unexpected error during Zabbix authentication (attempt {attempt + 1}): {str(e)}"
            )

        # Only sleep if we're going to retry
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    # If we get here, all retries failed
    zabbix_logger.critical(f"Zabbix authentication failed after {max_retries} attempts")
    raise ServiceErrorHandler("something went wrong please try again later")
