import logging
import requests
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class ZabbixServiceError(Exception):
pass

def create_host_group(self, name):
    for attempt in range(3):
        try:
            response = requests.post(
                f"{self.api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                json={
                    "jsonrpc": "2.0",
                    "method": "hostgroup.create",
                    "params": {"name": name},
                    "id": 1
                }
            )
            response.raise_for_status()
            result = response.json()

            if 'error' in result:
                logger.error(f"Host group creation failed: {result['error']['data']}")
                raise ZabbixServiceError(f"Host group creation error: {result['error']['data']}")

            return result['result']['groupids'][0]

        except Exception as e:
            logger.error(f"Host group creation failed: {str(e)}")
            time.sleep(2)

    raise ZabbixServiceError("host group creation failed after three attempts")