from typing import Any, cast

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zabbixproxy.models import ZabbixHostGroup, ZabbixUserGroup
from zabbixproxy.views.credentials.host_group_function import (
    ZabbixServiceError,
    create_host_group,
)
from zabbixproxy.views.credentials.user_group_function import create_user_group
from zabbixproxy.views.credentials.zabbiz_login_function import zabbix_login


class ZabbixCredentialsCreationWrapper(APIView):
    api_url = settings.ZABBIX_API_URL
    username = settings.ZABBIX_ADMIN_USER
    password = settings.ZABBIX_ADMIN_PASSWORD
    permission_classes = [IsAuthenticated]

    def get_zabbix_auth_token(self):
        try:
            return zabbix_login(
                api_url=self.api_url, username=self.username, password=self.password
            )
        except ZabbixServiceError as e:
            # Re-raise with more context
            raise ZabbixServiceError(
                f"Failed to obtain Zabbix authentication token: {str(e)}"
            )

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
        zabbix_host_group_name = f"{organization.organization_name}_zabbix_host_group"
        zabbix_user_group_name = f"{organization.organization_name}_zabbix_user_group"

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
                    "host_group": {
                        "id": existing_host_group.id,
                        "name": existing_host_group.name,
                        "zabbix_id": existing_host_group.hostgroupid,
                    },
                    "user_group": {
                        "id": existing_user_group.id,
                        "name": existing_user_group.name,
                        "zabbix_id": existing_user_group.usergroupid,
                        "permission": existing_user_group.permission,
                    },
                },
                status=status.HTTP_200_OK,
            )

        try:
            # Get auth token
            zabbix_auth_token = self.get_zabbix_auth_token()

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
                        self.api_url, zabbix_auth_token, zabbix_host_group_name
                    )

                    # Create host group record in our database
                    zabbix_host_group = cast(Any, ZabbixHostGroup).objects.create(
                        created_by=user,
                        name=zabbix_host_group_name,
                        hostgroupid=host_groupid,
                    )

                # Step 2: Create or get user group
                if existing_user_group:
                    zabbix_user_group = existing_user_group
                    user_groupid = existing_user_group.usergroupid
                else:
                    # Create user group in Zabbix with permissions for the host group
                    user_groupid = create_user_group(
                        self.api_url,
                        zabbix_auth_token,
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
                    "host_group": {
                        "id": zabbix_host_group.id,
                        "name": zabbix_host_group.name,
                        "zabbix_id": host_groupid,
                    },
                    "user_group": {
                        "id": zabbix_user_group.id,
                        "name": zabbix_user_group.name,
                        "zabbix_id": user_groupid,
                        "permission": permission
                        if not existing_user_group
                        else existing_user_group.permission,
                    },
                },
                status=status.HTTP_201_CREATED
                if not (existing_host_group and existing_user_group)
                else status.HTTP_200_OK,
            )

        except ZabbixServiceError as e:
            return Response(
                {"status": "error", "message": f"Zabbix service error: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
