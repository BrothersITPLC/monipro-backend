from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.models import OrganizationInfo
from customers.serializers import OrganizationPaymentUpdateSerializer


class OrganizationPaymentUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update organization payment plan and duration",
        operation_summary="Update organization payment information",
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description='Organization ID',
                required=True
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['organization_payment_plane', 'organization_payment_duration'],
            properties={
                'organization_payment_plane': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID of the payment plan to assign to the organization'
                ),
                'organization_payment_duration': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID of the payment duration (monthly, quarterly, yearly)'
                ),
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Status of the operation',
                        example='success'
                    ),
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Success message',
                        example='Payment plan updated successfully'
                    ),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Status of the operation',
                        example='error'
                    ),
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Error message',
                        example='Invalid data provided'
                    ),
                    'errors': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description='Detailed validation errors',
                        example={
                            'organization_payment_plane': ['Payment plan is required'],
                            'organization_payment_duration': ['Payment duration is required']
                        }
                    ),
                }
            ),
            status.HTTP_404_NOT_FOUND: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Status of the operation',
                        example='error'
                    ),
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Error message',
                        example='Organization not found'
                    ),
                }
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Status of the operation',
                        example='error'
                    ),
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Error message',
                        example='An error occurred while updating payment plan'
                    ),
                }
            ),
        },
        security=[{'Bearer': []}]
    )
    def patch(self, request, pk):
        try:
            organization = OrganizationInfo.objects.get(pk=pk)
            serializer = OrganizationPaymentUpdateSerializer(
                organization, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Payment plan updated successfully",
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "status": "error",
                    "message": "Invalid data provided",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except OrganizationInfo.DoesNotExist:
            return Response(
                {"status": "error", "message": "Organization not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "An error occurred while updating payment plan",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
