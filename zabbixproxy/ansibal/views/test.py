# ansibal/views/ansibal_runner.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils import ServiceErrorHandler
from zabbixproxy.ansibal.functions import create_zabbix_agent
from zabbixproxy.ansibal.serializers import AnsibleRequestSerializer


class AnsibleDeployView(APIView):
    def post(self, request):
        try:
            serializer = AnsibleRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            if "port" not in data:
                raise ServiceErrorHandler("Port is required")
            if "ip" not in data:
                if "dns" in data:
                    raise ServiceErrorHandler("Target host ip or dns is required")
            if "username" not in data:
                raise ServiceErrorHandler("Username is required")
            if "hostname" not in data:
                raise ServiceErrorHandler("Hostname is required")
            if "password" not in data:
                raise ServiceErrorHandler("Password is required")

            port = data["port"]
            target_host = data["ip"] or data["dns"]
            username = data["username"]
            hostname = data["hostname"]
            password = data["password"]
            tags = data["tags"]

            result = create_zabbix_agent(
                port, target_host, username, hostname, password, tags
            )
            return Response(
                {"status": "success", "message": "Zabbix agent created successfully", "result": result},
                status=status.HTTP_201_CREATED,
            )

        except ServiceErrorHandler as e:
            return Response(
                {"status": "error", "message": f"{str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
