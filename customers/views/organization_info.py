# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.serializers import OrganizationInfoSerializer
from utils import ServiceErrorHandler


class OrganizationInfoCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrganizationInfoSerializer(
            data=request.data,
            context={'request': request}
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
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
