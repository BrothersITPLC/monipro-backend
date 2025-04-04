from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zabbixproxy.models import ZabbixHostGroup, ZabbixUser, ZabbixUserGroup


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Base user data
        user_data = {
            "user_id": user.id,
            "user_name": user.name,
            "user_email": user.email,
            "is_private": user.is_private,
            "is_organization": user.role == "is_organization",
            "organization_info_completed": user.is_organization_completed_information,
        }

        if (
            cast(Any, ZabbixHostGroup).objects.filter(created_by=user).exists()
            and cast(Any, ZabbixUserGroup).objects.filter(created_by=user).exists()
        ):
            user_data.update(
                {
                    "user_have_zabbix_credentials_1": True,
                }
            )

            if cast(Any, ZabbixUser).objects.filter(user=user).exists():
                user_data.update(
                    {
                        "user_have_zabbix_user": True,
                    }
                )
            else:
                user_data.update(
                    {
                        "user_have_zabbix_user": False,
                    }
                )
        else:
            user_data.update(
                {
                    "user_have_zabbix_credentials_1": False,
                }
            )

        # Add personal info if not organization
        if user.role != "is_organization":
            user_data.update(
                {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone,
                }
            )

        # Add organization info if completed
        if user.is_organization_completed_information and user.organization:
            org = user.organization
            user_data.update(
                {
                    "organization_id": org.id,
                    "organization_name": org.organization_name,
                    "organization_phone": org.organization_phone,
                    "organization_website": org.organization_website,
                    "organization_description": org.organization_description,
                    "organization_payment_plane": org.organization_payment_plane.name
                    if org.organization_payment_plane
                    else None,
                    "organization_payment_duration": org.organization_payment_duration.name
                    if org.organization_payment_duration
                    else None,
                }
            )

        return Response(
            {"status": "success", "user_data": user_data}, status=status.HTTP_200_OK
        )
