import logging
import requests
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class ZabbixServiceError(Exception):
pass


def create_user_group(self, name, hostgroup_id):
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
                    "method": "usergroup.create",
                    "params": {
                        "name": name,
                        "hostgroup_rights": {
                            "id": hostgroup_id,
                            "permission": 0
                        }
                    },
                    "id": 1
                }
            )
            response.raise_for_status()
            result = response.json()

            if 'error' in result:
                logger.error(f"User group creation failed: {result['error']['data']}")
                raise ZabbixServiceError(f"User group creation error: {result['error']['data']}")

            return result['result']['usrgrpids'][0]

        except Exception as e:
            logger.error(f"User group creation failed: {str(e)}")
            raise

    raise ZabbixServiceError("User group creation failed after three attempts")