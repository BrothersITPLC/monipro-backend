import logging

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import AddUserSerializer
from utils import ServiceErrorHandler, generate_password, send_team_user_creation_email
from zabbixproxy.models import ZabbixAuthToken, ZabbixUserGroup
from zabbixproxy.serializers import ZabbixUserSerializer
from zabbixproxy.views.credentials.functions import create_user, zabbix_login

django_logger = logging.getLogger("django")
zabbix_logger = logging.getLogger("zabbix")


class AddUserView(APIView):
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
        except ServiceErrorHandler as e:
            raise ServiceErrorHandler(f"{str(e)}")

    def post(self, request):
        try:
            admin_user = request.user
            organization = admin_user.organization

            if organization is None:
                return Response(
                    {
                        "status": "error",
                        "message": "You are not part of any organization to make this request.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_group = ZabbixUserGroup.objects.filter(created_by=admin_user).first()

            if user_group is None:
                return Response(
                    {
                        "status": "error",
                        "message": "You are not part of any user group to make this request.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            password = generate_password(8)
            if not password:
                return Response(
                    {
                        "status": "error",
                        "message": "Something went wrong. Please try again.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            email = request.data.get("email")
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")
            role = request.data.get("is_admin")

            if not email or not first_name or not last_name or role is None:
                return Response(
                    {
                        "status": "error",
                        "message": "Missing required fields: email, first name, last name, or role.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            roleid = 1 if role else 0

            name = f"{first_name} {last_name}"
            organization_name = organization.organization_name

            with transaction.atomic():
                auth_token = ZabbixAuthToken.objects.first()
                if not auth_token:
                    auth_token = ZabbixAuthToken.get_or_create_token(
                        self.get_zabbix_auth_token()
                    )

                # 1. Create user in Zabbix
                userid = create_user(
                    self.api_url,
                    auth_token,
                    username=email,
                    password=password,
                    roleid=roleid,
                    usergroup_id=user_group.usergroupid,
                )

                # 2. Send welcome email
                success, message = send_team_user_creation_email(
                    email, name, organization_name, password
                )
                if not success:
                    raise ServiceErrorHandler(f"Failed to send email: {message}")

                # 3. Create user in local DB

                user_serializer = AddUserSerializer(
                    data=request.data,
                    context={
                        "password": password,
                        "organization": organization,
                        "is_verified": True,
                        "is_active": True,
                    },
                )
                user_serializer.is_valid(raise_exception=True)
                user = user_serializer.save()

                # 4. Create ZabbixUser in local DB

                zabbix_user_data = {
                    "username": email,
                    "password": password,
                    "userid": userid,
                }

                zabbix_user_serializer = ZabbixUserSerializer(
                    data=zabbix_user_data,
                    context={
                        "user": user,
                        "user_group": user_group,
                        "roleid": roleid,
                    },
                )

                zabbix_user_serializer.is_valid(raise_exception=True)
                zabbix_user_serializer.save()

            return Response(
                {
                    "status": "success",
                    "message": "user created successfully.",
                },
                status=status.HTTP_200_OK,
            )

        except ServiceErrorHandler as e:
            django_logger.error(f"AddUserView error: {str(e)}")
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            django_logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "message": "something went wrong please try again later",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
