import logging
import time

import requests

zabbix_logger = logging.getLogger("zabbix")
django_logger = logging.getLogger("django")

from utils import ServiceErrorHandler


def create_user(
    api_url,
    auth_token,
    username,
    password,
    roleid,
    usergroup_id,
    max_retries=3,
    retry_delay=2,
):
    """
    Create a user in Zabbix.

    Args:
        api_url: Zabbix API URL
        auth_token: Zabbix authentication token
        username: Username for the new user (typically email)
        password: Password for the new user
        roleid: Role ID for the user (1 for admin, 0 for user)
        usergroup_id: User group ID to assign the user to
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        User ID string

    Raises:
        ServiceErrorHandler: If user creation fails after max_retries
    """
    for attempt in range(max_retries):
        try:
            zabbix_logger.info(
                f"Attempting to create user '{username}' (attempt {attempt + 1}/{max_retries})"
            )

            response = requests.post(
                f"{api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}",
                },
                json={
                    "jsonrpc": "2.0",
                    "method": "user.create",
                    "params": {
                        "username": username,
                        "passwd": password,
                        "roleid": roleid,
                        "usrgrps": [{"usrgrpid": usergroup_id}],
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
            # Success case
            userid = result["result"]["userids"][0]
            zabbix_logger.info(f"User '{username}' created successfully with ID: {userid}")
            return userid

        except requests.RequestException as e:
            zabbix_logger.error(
                f"Network error during user creation (attempt {attempt + 1}): {str(e)}"
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
                    "Authentication error during user creation, token may be invalid"
                )
                raise
            zabbix_logger.error(f"Zabbix service error (attempt {attempt + 1}): {str(e)}")
        except Exception as e:
            zabbix_logger.error(
                f"Unexpected error during user creation (attempt {attempt + 1}): {str(e)}"
            )

        # Only sleep if we're going to retry
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    # If we get here, all retries failed
    zabbix_logger.critical(f"User creation failed after {max_retries} attempts")
    raise ServiceErrorHandler(f"User creation failed after {max_retries} attempts")
