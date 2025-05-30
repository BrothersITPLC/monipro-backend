import logging

import requests
from django.conf import settings

from utils import ServiceErrorHandler
from zabbixproxy.credentials_functions import zabbix_login

api_url = settings.ZABBIX_API_URL
username = settings.ZABBIX_ADMIN_USER
password = settings.ZABBIX_ADMIN_PASSWORD

zabbix_logger = logging.getLogger("zabbix")
django_logger = logging.getLogger("django")


def get_zabbix_auth_token(self):
    try:
        return zabbix_login(
            api_url=self.api_url, username=self.username, password=self.password
        )
    except ServiceErrorHandler as e:
        raise ServiceErrorHandler(f"{str(e)}")


def get_real_time_data(itemids, value_type, hostids):
    """
    Get real-time data from Zabbix API.
    Returns: Dictionary containing the response data or raises ServiceErrorHandler
    """
    try:
        if not itemids:
            raise ServiceErrorHandler("Missing itemids parameter")

        # Get auth token using the zabbix_login function
        auth_token = get_zabbix_auth_token()

        # Prepare the request to Zabbix API
        zabbix_request = {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "hostids": hostids,
                "output": "extend",
                "history": value_type,
                "itemids": itemids,
                "limit": 100,
                "sortfield": "clock",
                "sortorder": "DESC",
            },
            "id": 3,
        }

        # Make the request to Zabbix API
        response = requests.post(
            f"{api_url}/api_jsonrpc.php",
            json=zabbix_request,
            headers={
                "Content-Type": "application/json-rpc",
                "Authorization": f"Bearer {auth_token}",
            },
            timeout=15,
        )

        try:
            response_data = response.json()
        except ValueError:
            zabbix_logger.error("Invalid JSON received from Zabbix.")
            raise ServiceErrorHandler("Invalid response from Zabbix API")

        if "error" in response_data:
            error_info = response_data["error"]
            error_code = error_info.get("code", "N/A")
            error_message = error_info.get("message", "No message")
            error_data = error_info.get("data", "")

            zabbix_logger.error(
                f"Zabbix API Error [{error_code}]: {error_message} - {error_data}"
            )
            raise ServiceErrorHandler(f"{error_message} - {error_data}")

        return response_data

    except requests.RequestException as e:
        zabbix_logger.error(f"Request error: {str(e)}")
        raise ServiceErrorHandler("Failed to connect to Zabbix API")
    except Exception as e:
        django_logger.exception(f"Unexpected error in get_real_time_data: {str(e)}")
        raise ServiceErrorHandler("Unexpected error occurred")
