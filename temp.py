import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from ..serializers import VerifyRegistrationOtpSerializer
from ..services.zabbix_service import ZabbixService, ZabbixServiceError

logger = logging.getLogger(__name__)

class VerifyRegistrationOtp(APIView):
    def post(self, request):
        serializer = VerifyRegistrationOtpSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            otp_instance = serializer.validated_data["otp_instance"]

            otp_instance.is_used = True
            otp_instance.save()

            user.is_verified = True
            user.save()

            if otp_instance.is_used and user.is_verified:
                try:
                    zabbix_service = ZabbixService()
                    auth_token = zabbix_service.authenticate()

                    # Create host group with user-specific name
                    hostgroup_name = f"{user.email}-servers"
                    hostgroup_id = zabbix_service.create_host_group(hostgroup_name)
                    
                    # Create user group with user-specific name
                    usergroup_name = f"{user.email}-operators"
                    usergroup_id = zabbix_service.create_user_group(usergroup_name, hostgroup_id)

                    # Create Zabbix user
                    zabbix_user_id = zabbix_service.create_user(user.email, usergroup_id)
                    
                    # Update Django user with Zabbix credentials
                    user.zabbix_userid = zabbix_user_id
                    user.zabbix_hostgroup = hostgroup_id
                    user.zabbix_usergroup = usergroup_id
                    user.save()
                    
                    return Response(
                        {
                            "status": "success",
                            "message": "OTP verified and Zabbix integration completed successfully.",
                            "user_id": user.id,
                            "zabbix_userid": zabbix_user_id,
                            "hostgroup_id": hostgroup_id,
                            "usergroup_id": usergroup_id
                        },
                        status=status.HTTP_202_ACCEPTED,
                    )
                    
                except ZabbixServiceError as e:
                    logger.error(f"Zabbix integration failed: {str(e)}")
                    return Response(
                        {
                            "status": "error",
                            "message": f"OTP verified but Zabbix integration failed: {str(e)}"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                except Exception as e:
                    logger.error(f"Unexpected error during Zabbix integration: {str(e)}")
                    return Response(
                        {
                            "status": "error",
                            "message": "OTP verified but an unexpected error occurred during Zabbix integration."
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

        return Response(
            {
                "status": "error",
                "message": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

  
    # Zabbix integration fields

