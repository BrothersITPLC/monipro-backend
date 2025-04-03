import logging
import requests
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class ZabbixServiceError(Exception):
    pass
    
class ZabbixService:
    def __init__(self):
        self.api_url = settings.ZABBIX_API_URL
        self.auth_token = None

    def authenticate(self):
        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.api_url}/api_jsonrpc.php",
                    json={
                        "jsonrpc": "2.0",
                        "method": "user.login",
                        "params": {
                            "username": settings.ZABBIX_ADMIN_USER,
                            "password": settings.ZABBIX_ADMIN_PASSWORD
                        },
                        "id": 1
                    }
                )
                response.raise_for_status()
                result = response.json()

                if 'error' in result:
                    raise ZabbixServiceError(f"Auth error: {result['error']['data']}")

                self.auth_token = result['result']
                return self.auth_token

            except Exception as e:
                logger.error(f"Zabbix authentication failed (attempt {attempt + 1}): {str(e)}")
                time.sleep(2)

        raise ZabbixServiceError("Zabbix authentication failed after 3 attempts")