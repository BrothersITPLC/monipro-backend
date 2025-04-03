from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from ..services.zabbix_service import ZabbixService, ZabbixServiceError

class ZabbixDataView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({
                    'status': 'error',
                    'message': 'Authentication required',
                    'code': 'AUTH_REQUIRED'
                }, status=status.HTTP_401_UNAUTHORIZED)

            if not hasattr(request.user, 'organization') or not request.user.organization:
                return Response({
                    'status': 'error',
                    'message': 'User organization not found',
                    'code': 'ORG_NOT_FOUND'
                }, status=status.HTTP_404_NOT_FOUND)

            # Initialize Zabbix service
            zabbix_service = ZabbixService()
            
            try:
                # Authenticate with Zabbix
                zabbix_service.authenticate()
            except ZabbixServiceError as e:
                return Response({
                    'status': 'error',
                    'message': str(e),
                    'code': 'ZABBIX_AUTH_ERROR'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            try:
                # Get the user's organization's host group ID from their profile
                hostgroup_id = request.user.organization.zabbix_hostgroup_id
                if not hostgroup_id:
                    return Response({
                        'status': 'error',
                        'message': 'Zabbix host group not configured for organization',
                        'code': 'HOSTGROUP_NOT_CONFIGURED'
                    }, status=status.HTTP_404_NOT_FOUND)
            except ObjectDoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Organization profile not found',
                    'code': 'ORG_PROFILE_NOT_FOUND'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Fetch host data from Zabbix
            try:
                host_data = zabbix_service.get_host_data()
                return Response({
                    'status': 'success',
                    'data': host_data
                }, status=status.HTTP_200_OK)
            except ZabbixServiceError as e:
                return Response({
                    'status': 'error',
                    'message': str(e),
                    'code': 'ZABBIX_HOST_DATA_ERROR'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except ZabbixServiceError as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'code': 'ZABBIX_SERVICE_ERROR'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'code': 'INTERNAL_SERVER_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)