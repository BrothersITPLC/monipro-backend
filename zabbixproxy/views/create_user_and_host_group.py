from typing import Any, cast

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils import ServiceErrorHandler
from zabbixproxy.functions.credentials_functions import (
    create_host_group,
    create_user_group,
    zabbix_login,
)
from zabbixproxy.models import ZabbixHostGroup, ZabbixUserGroup


class HostAndUserGroupCreationView(APIView):
    api_url = settings.ZABBIX_API_URL
    username = settings.ZABBIX_ADMIN_USER
    password = settings.ZABBIX_ADMIN_PASSWORD
    permission_classes = [IsAuthenticated]

    def get_zabbix_auth_token(self):
        try:
            return zabbix_login(
                api_url=self.api_url, username=self.username, password=self.password
            )
        except ServiceErrorHandler as e:
            raise ServiceErrorHandler(f"{str(e)}")

    def post(self, request):
        """Creates a Zabbix Host Group and User Group for the authenticated user's organization."""
        user = request.user

        # Get organization from user
        organization = getattr(user, "organization", None)
        if not organization:
            return Response(
                {"error": "User has no associated organization"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create names for host group and user group
        zabbix_host_group_name = f"{user.email}_zabbix_host_group"
        zabbix_user_group_name = f"{user.email}_zabbix_user_group"

        # Default values
        permission = 3  # read-write permission for user group

        # Check if host group already exists for this user
        existing_host_group = (
            cast(Any, ZabbixHostGroup)
            .objects.filter(created_by=user, name=zabbix_host_group_name)
            .first()
        )

        # Check if user group already exists for this user
        existing_user_group = (
            cast(Any, ZabbixUserGroup)
            .objects.filter(created_by=user, name=zabbix_user_group_name)
            .first()
        )

        # If both already exist, return them
        if existing_host_group and existing_user_group:
            return Response(
                {
                    "status": "success",
                    "message": "Zabbix resources already exist",
                },
                status=status.HTTP_200_OK,
            )
        try:

            auth_token = self.get_zabbix_auth_token()
            # Fix for transaction.atomic() type issue
            atomic_context = cast(Any, transaction.atomic())

            # Use transaction to ensure database consistency
            with atomic_context:
                # Step 1: Create or get host group
                if existing_host_group:
                    zabbix_host_group = existing_host_group
                    host_groupid = existing_host_group.hostgroupid
                else:
                    # Create host group in Zabbix
                    host_groupid = create_host_group(
                        self.api_url, auth_token, zabbix_host_group_name
                    )

                    # Create host group record in our database
                    zabbix_host_group = cast(Any, ZabbixHostGroup).objects.create(
                        created_by=user,
                        name=zabbix_host_group_name,
                        hostgroupid=host_groupid,
                        belongs_to=user.organization,
                    )

                # Step 2: Create or get user group
                if existing_user_group:
                    zabbix_user_group = existing_user_group
                    user_groupid = existing_user_group.usergroupid
                else:
                    # Create user group in Zabbix with permissions for the host group
                    user_groupid = create_user_group(
                        self.api_url,
                        auth_token,
                        zabbix_user_group_name,
                        host_groupid,
                        permission,
                    )

                    # Create user group record in our database
                    zabbix_user_group = cast(Any, ZabbixUserGroup).objects.create(
                        created_by=user,
                        name=zabbix_user_group_name,
                        usergroupid=user_groupid,
                        hostgroupid=zabbix_host_group,
                        permission=str(permission),
                    )

            # Return success response with created resources
            return Response(
                {
                    "status": "success",
                    "message": "Zabbix resources created successfully",
                },
                status=(
                    status.HTTP_201_CREATED
                    if not (existing_host_group and existing_user_group)
                    else status.HTTP_200_OK
                ),
            )

        except ServiceErrorHandler as e:
            return Response(
                {"status": "error", "message": f"Zabbix service error: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception:
            return Response(
                {"status": "error", "message": "Unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
