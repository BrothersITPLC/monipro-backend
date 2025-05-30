import ipaddress
import logging
import re

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zabbixproxy.check_reachability_functions import check_reachability

django_logger = logging.getLogger("django")

DOMAIN_REGEX = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
)


class CheckReachabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Check if a host is reachable via ICMP ping or DNS resolution.
        Expects 'host' and 'is_domain' parameters in the query string.
        """
        host = request.query_params.get("host")
        is_domain = request.query_params.get("is_domain", "false").lower() == "true"

        # Validate presence
        if not host:
            return Response(
                {"status": "error", "message": "Missing 'host' parameter"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate format
        if is_domain:
            if not DOMAIN_REGEX.fullmatch(host):
                return Response(
                    {"status": "error", "message": "Invalid domain format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            try:
                ipaddress.ip_address(host)
            except ValueError:
                return Response(
                    {"status": "error", "message": "Invalid IP address format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            reachable = check_reachability(is_domain, host)
            print(f"Reachability check for {host} (is_domain={is_domain}): {reachable}")
            if not reachable:
                return Response(
                    {"status": "error", "message": "Host is not reachable"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"status": "success", "message": "Host is reachable"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            django_logger.error(f"Error checking reachability: {e}")
            return Response(
                {
                    "status": "error",
                    "message": "Error checking reachability, try again later",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
