import json
import logging

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from zabbixproxy.views.zabbiz_login import ZabbixServiceError, zabbix_login

api_url = settings.ZABBIX_API_URL
username = settings.ZABBIX_ADMIN_USER
password = settings.ZABBIX_ADMIN_PASSWORD

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def get_host_items(request):
    """
    Proxy endpoint to get host items from Zabbix API.
    Frontend only needs to send the hostids.
    """
    try:
        # Parse request data
        data = json.loads(request.body)
        hostids = data.get("hostids")

        if not hostids:
            return JsonResponse({"error": "Missing hostids parameter"}, status=400)

        # Get auth token using the zabbix_login function
        try:
            auth_token = zabbix_login(api_url, username, password)
        except ZabbixServiceError as e:
            logger.error(f"Failed to authenticate with Zabbix: {str(e)}")
            return JsonResponse(
                {"error": "Failed to authenticate with Zabbix"}, status=500
            )

        # Prepare the request to Zabbix API
        zabbix_request = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["itemid", "name", "key_"],
                "hostids": hostids,
                "search": {
                    "name": "CPU",
                },
                "sortfield": "name",
            },
            "id": 2,
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

        # Check for HTTP errors
        if response.status_code != 200:
            logger.error(f"HTTP error from Zabbix API: {response.status_code}")
            return JsonResponse(
                {"error": f"Zabbix API returned HTTP {response.status_code}"},
                status=502,
            )

        # Parse the response
        result = response.json()

        # Check for API errors
        if "error" in result:
            error_message = result["error"].get(
                "data", result["error"].get("message", "Unknown error")
            )
            logger.error(f"Zabbix API error: {error_message}")
            return JsonResponse(
                {"error": f"Zabbix API error: {error_message}"}, status=502
            )

        # Return the result directly
        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        logger.exception(f"Unexpected error in get_host_items: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)
