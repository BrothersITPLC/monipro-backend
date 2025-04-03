import logging
import requests
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class ZabbixServiceError(Exception):
pass

def create_user(self, email, usergroup_id):
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
                    "method": "user.create",
                    "params": {
                        "username": email,
                        "passwd": settings.ZABBIX_DEFAULT_PASSWORD,
                        "roleid": "2",
                        "usrgrps": [{
                            "usrgrpid": usergroup_id
                        }]
                    },
                    "id": 1
                }
            )
            response.raise_for_status()
            result = response.json()

            if 'error' in result:
                logger.error(f"User creation failed: {result['error']['data']}")
                raise ZabbixServiceError(f"User creation error: {result['error']['data']}")

            return result['result']['userids'][0]

        except Exception as e:
            logger.error(f"User creation failed: {str(e)}")
            time.sleep(2)
            
    raise ZabbixServiceError("User creation failed after three attempts")