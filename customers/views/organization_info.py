# views.py
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.serializers import OrganizationInfoSerializer
from utils import ServiceErrorHandler


class OrganizationInfoCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Create or update organization profile information",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "user_id",
                "organization_phone",
                "organization_payment_plan",
                "organization_payment_duration",
                "is_private",
            ],
            properties={
                "user_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the user associated with this organization",
                ),
                "organization_phone": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Ethiopian phone number starting with +251 followed by 9 digits (first digit 7 or 9)",
                ),
                "organization_website": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Organization website URL",
                    nullable=True,
                ),
                "organization_description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Description of the organization",
                    nullable=True,
                ),
                "organization_payment_plan": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the payment plan"
                ),
                "organization_payment_duration": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the payment duration"
                ),
                "is_private": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Whether this is a private organization",
                ),
                "first_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Required if is_private=true",
                    nullable=True,
                ),
                "last_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Required if is_private=true",
                    nullable=True,
                ),
                "organization_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Required if is_private=false",
                    nullable=True,
                ),
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Status of the operation",
                        example="success",
                    ),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Success message",
                        example="Profile updated successfully",
                    ),
                },
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Status of the operation",
                        example="error",
                    ),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Error message",
                        example="Organization phone is required, Payment provider is required",
                    ),
                },
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Status of the operation",
                        example="error",
                    ),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Error message",
                        example="An unexpected error occurred",
                    ),
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = OrganizationInfoSerializer(
            data=request.data, context={"request": request}
        )

        try:
            serializer.is_valid(raise_exception=True)
            organization = serializer.save()

            return Response(
                {
                    "status": "success",
                    "message": " Profile updated successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        except ServiceErrorHandler as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            if "phone" in str(e).lower():
                return Response(
                    {
                        "status": "error",
                        "message": "Ethiopian phone number starting with +251 followed by 9 digits (first digit 7 or 9)",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            print(f"Unexpected error: {e}")

            return Response(
                {"status": "error", "message": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
