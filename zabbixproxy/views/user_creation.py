from typing import Any, cast

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zabbixproxy.models import ZabbixUser, ZabbixUserGroup
from zabbixproxy.views.user import ZabbixServiceError, create_user
from zabbixproxy.views.zabbiz_login import zabbix_login


class ZabbixUserCreationView(APIView):
    api_url = settings.ZABBIX_API_URL
    username = settings.ZABBIX_ADMIN_USER
    password = settings.ZABBIX_ADMIN_PASSWORD
    default_password = settings.ZABBIX_DEFAULT_PASSWORD
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
        """Creates a Zabbix User for the authenticated user."""
        user = request.user

        # Get user group from request or user's organization
        user_group = (
            cast(Any, ZabbixUserGroup).objects.filter(created_by=request.user).first()
        )
        if not user_group:
            return Response(
                {"error": "No user group found for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use first_name + last_name as Zabbix username
        zabbix_username = f"{user.first_name}{user.last_name}"
        if not zabbix_username.strip():
            # Fallback to email if name is empty
            zabbix_username = user.email

        # Default role is admin (1)
        roleid = request.data.get("roleid", 1)

        # Check if user already exists
        existing_user = (
            cast(Any, ZabbixUser)
            .objects.filter(user=user, user_group=user_group)
            .first()
        )

        if existing_user:
            return Response(
                {
                    "status": "success",
                    "message": "Zabbix user already exists",
                    "user": {
                        "id": existing_user.id,
                        "username": existing_user.username,
                        "zabbix_id": existing_user.userid,
                        "role": existing_user.roleid,
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
                # Create user in Zabbix
                userid = create_user(
                    self.api_url,
                    zabbix_auth_token,
                    username=zabbix_username,
                    password=self.default_password,
                    roleid=roleid,
                    usergroup_id=user_group.usergroupid,
                )

                # Create user record in our database
                zabbix_user = cast(Any, ZabbixUser).objects.create(
                    user=user,
                    userid=userid,
                    user_group=user_group,
                    username=zabbix_username,
                    password=self.default_password,
                    roleid=str(roleid),  # Convert to string to match model field
                )

            # Return success response
            return Response(
                {
                    "status": "success",
                    "message": "Zabbix user created successfully",
                    "user": {
                        "id": zabbix_user.id,
                        "username": zabbix_user.username,
                        "zabbix_id": userid,
                        "role": roleid,
                    },
                },
                status=status.HTTP_201_CREATED,
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
