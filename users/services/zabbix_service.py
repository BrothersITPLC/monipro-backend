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

    def create_host_group(self, name):
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
            raise

    def create_user_group(self, name, hostgroup_id):
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

    def create_user(self, email, usergroup_id):
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
            raise

    def get_host_data(self):
        try:
            response = requests.post(
                f"{self.api_url}/api_jsonrpc.php",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                json={
                    "jsonrpc": "2.0",
                    "method": "user.get",
                    "params": {
                        "output": "extend",
                    },
                    "id": 1
                }
            )
            response.raise_for_status()
            result = response.json()

            print(auth_token)

            if 'error' in result:
                logger.error(f"Host data retrieval failed: {result['error']['data']}")
                raise ZabbixServiceError(f"Host data retrieval error: {result['error']['data']}")

            return result['result']

        except Exception as e:
            logger.error(f"Host data retrieval failed: {str(e)}")
            raise