import requests


def get_single_alerts(triggerid):

    zabbix_api_url = "https://zx.brothersit.dev/api_jsonrpc.php"
    auth_token = "98822a8062620e621d93240ce8ad0be8"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }
    payload = {
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "triggerids": triggerid,
            "output": "extend",
            "selectHosts": ["hostid", "host"],
            "selectTags": "extend",
            "expandDescription": 1
        },
        "id": 1
    }

    try:
        response = requests.post(zabbix_api_url, json=payload, headers=headers).json()
        alert_data = response.get("result", [{}])[0]
        
        return {
            "trigger": {
                "description": alert_data.get("description"),
                "priority": alert_data.get("priority"),
                "lastchange": alert_data.get("lastchange"),
                "comments": alert_data.get("comments"),
                "event_name": alert_data.get("event_name"),
                "value": alert_data.get("value")
            },
            "host": alert_data.get("hosts", [{}])[0],
            "items": [],  # Add item data if needed
            "tags": alert_data.get("tags", [])
        }
        
    except Exception as e:
        return {"error": f"error from zabbix{str(e)}" }

