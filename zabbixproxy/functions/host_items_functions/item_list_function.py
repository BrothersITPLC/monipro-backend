import json
import logging

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from utils import ServiceErrorHandler
from zabbixproxy.functions.credentials_functions import zabbix_login
from zabbixproxy.functions.host_items_functions import get_real_time_data

api_url = settings.ZABBIX_API_URL
username = settings.ZABBIX_ADMIN_USER
password = settings.ZABBIX_ADMIN_PASSWORD

zabbix_logger = logging.getLogger("zabbix")
django_logger = logging.getLogger("django")


def get_zabbix_auth_token():
    try:
        return zabbix_login(api_url=api_url, username=username, password=password)
    except ServiceErrorHandler as e:
        raise ServiceErrorHandler(f"{str(e)}")


@csrf_exempt
@require_GET
def get_host_items(request):
    """
    Proxy endpoint to get host items from Zabbix API.
    Frontend only needs to send the hostids and name as query parameters.
    """
    try:
        hostids = request.GET.get("hostids")
        name = request.GET.get("name", "CPU")

        if not hostids:
            return JsonResponse({"error": "Missing hostids parameter"}, status=400)

        auth_token = get_zabbix_auth_token()

        zabbix_request = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["itemid", "name", "key_", "value_type", "units"],
                "hostids": hostids,
                "search": {
                    "name": name,
                },
                "sortfield": "name",
            },
            "id": 2,
        }

        response = requests.post(
            f"{api_url}/api_jsonrpc.php",
            json=zabbix_request,
            headers={
                "Content-Type": "application/json-rpc",
                "Authorization": f"Bearer {auth_token}",
            },
            timeout=15,
        )

        try:
            response_data_for_log = response.json()
        except ValueError:
            zabbix_logger.error("Invalid JSON received from Zabbix.")
            raise ServiceErrorHandler("Host creation please try again later")

        if "error" in response_data_for_log:
            error_info = response_data_for_log["error"]
            error_code = error_info.get("code", "N/A")
            error_message = error_info.get("message", "No message")
            error_data = error_info.get("data", "")

            zabbix_logger.error(
                f"Zabbix API Error [{error_code}]: {error_message} - {error_data}"
            )

            return JsonResponse(
                {
                    "status": "error",
                    "message": f"{error_message} - {error_data}",
                },
                status=502,
            )

        # Parse the response
        result = response.json()
        # Return the result directly
        compiled_response = {
            "status": "success",
            "data": [],
        }

        try:
            for item in result["result"]:
                item_content_result_data = []
                item_content_result = get_real_time_data(
                    itemids=item["itemid"],
                    value_type=item["value_type"],
                    hostids=hostids,
                )
                if item_content_result.get("result"):
                    item_content_result_data = item_content_result["result"]
                    compiled_response["data"].append(
                        {
                            "itemid": item["itemid"],
                            "name": item["name"],
                            "value_type": item["value_type"],
                            "units": item["units"],
                            "result": item_content_result_data,
                        }
                    )

        except Exception as e:
            django_logger.exception(f"Error processing item: {str(e)}")

        return JsonResponse(compiled_response)

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "status": "error",
                "message": "Invalid JSON in request body",
            },
            status=400,
        )
    except Exception as e:
        django_logger.exception(f"Unexpected error in get_real_time_data: {str(e)}")
        return JsonResponse(
            {
                "status": "error",
                "message": "Unexpected error occurred",
            },
            status=500,
        )
