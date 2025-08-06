import json
import logging
import time

import requests
from django.conf import settings

from utils import ServiceErrorHandler

zabbix_logger = logging.getLogger("zabbix")

api_url = settings.ZABBIX_API_URL
username = settings.ZABBIX_ADMIN_USER
password = settings.ZABBIX_ADMIN_PASSWORD


def send_request(method, params, max_retries=3, retry_delay=2):
    """
    Send a request to the Zabbix API with retry logic and error handling.
    """
    zabbix_base_url = f"{api_url}/api_jsonrpc.php"
    auth_token = "95031fec58f895d7b52a7d49ed7e719b"

    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }

    for attempt in range(max_retries):
        try:
            zabbix_logger.info(f"Zabbix API call '{method}' (attempt {attempt})")
            response = requests.post(
                zabbix_base_url, data=json.dumps(payload), headers=headers, timeout=10
            )

            zabbix_logger.debug(f"Response status code: {response.status_code}")
            response.raise_for_status()

            if not response.text:
                raise ServiceErrorHandler("Empty response from Zabbix API")

            try:
                result = response.json()
            except json.JSONDecodeError as e:
                raise ServiceErrorHandler(
                    f"Invalid JSON from Zabbix: {e}\nContent: {response.text[:500]}"
                )

            if "error" in result:
                raise ServiceErrorHandler(
                    f"Zabbix API Error: {result['error']['message']} - {result['error']['data']}"
                )
            return result.get("result", [])

        except (requests.exceptions.RequestException, ServiceErrorHandler) as e:
            zabbix_logger.warning(f"Request attempt {attempt} failed: {e}")

            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise ServiceErrorHandler(
                    f"Zabbix API request failed after {max_retries} attempts: {e}"
                )
        except Exception as e:
            zabbix_logger.exception("Unexpected error during Zabbix API call")
            raise ServiceErrorHandler("Unexpected error, please try again later")
