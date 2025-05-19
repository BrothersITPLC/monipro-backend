import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def get_zabbix_alerts(request):
    host_ids = [10655, 10698, 10663]

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
            "output": [
                "triggerid",
                "description",
                "lastchange",
                "priority",
                "status",
                "value",
                "comments",
                "event_name",
                "tags",
            ],
            "selectHosts": ["hostid", "host"],
            "hostids": host_ids,
            "sortfield": "lastchange",
            "sortorder": "DESC",
        },
        "id": 1,
    }

    response = requests.post(
        zabbix_api_url, json=payload, headers=headers, verify=False
    )

    if response.status_code != 200:
        return JsonResponse({"error": "Zabbix API request failed"}, status=500)

    data = response.json()
    if "error" in data:
        return JsonResponse({"error": data["error"]["data"]}, status=500)

    alerts = data.get("result", [])

    # Group alerts by host name
    host_alerts = {}

    for alert in alerts:
        try:
            host = alert.get("hosts", [{}])[0].get("host", "N/A")
            if host not in host_alerts:
                host_alerts[host] = {"active": [], "inactive": []}

            common_data = {
                "id": alert["triggerid"],
                "description": alert.get("description", "No description"),
                "severity": map_severity(int(alert.get("priority", 0))),
                "comments": alert.get("comments", "No comments"),
                "event_name": alert.get("event_name", "No event name"),
                "timestamp": alert.get("lastchange", 0),
            }

            if alert.get("value") == "1":
                host_alerts[host]["active"].append(common_data)
            else:
                host_alerts[host]["inactive"].append(common_data)
        except (KeyError, IndexError) as e:
            print(f"Error processing alert: {e}")
            continue

    return JsonResponse(host_alerts, safe=False)


def map_severity(level):
    severity_map = {
        0: "Unclassified",
        1: "Information",
        2: "Warning",
        3: "Average",
        4: "High",
        5: "Disaster",
    }
    return severity_map.get(level, "Unknown")
