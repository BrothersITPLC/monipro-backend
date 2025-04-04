import json
import logging

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from zabbixproxy.views.credentials.zabbiz_login_function import (
    ZabbixServiceError,
    zabbix_login,
)

api_url = settings.ZABBIX_API_URL
username = settings.ZABBIX_ADMIN_USER
password = settings.ZABBIX_ADMIN_PASSWORD

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def get_real_time_data(request):
    """
    Proxy endpoint to get real-time data from Zabbix API.
    Frontend only needs to send the itemids.
    """
    try:
        # Parse request data
        data = json.loads(request.body)
        itemids = data.get("itemids")

        if not itemids:
            return JsonResponse({"error": "Missing itemids parameter"}, status=400)

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
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": 0,  # Assuming we're fetching numeric data
                "itemids": itemids,
                "limit": 100,  # Fetch the last 100 data points for historical data
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
        logger.exception(f"Unexpected error in get_real_time_data: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)
