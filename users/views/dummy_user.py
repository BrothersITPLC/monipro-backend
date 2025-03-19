from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import DummyUser
from users.serializers import DummyUserSerializer


class DummyUserView(APIView):
    """
    API View for DummyUser model to handle CRUD operations
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get a list of dummy users, optionally filtered by organization_id
        """
        organization_id = request.query_params.get("organization_id", None)

        if organization_id and request.path.endswith("/by-organization/"):
            # Handle the by_organization endpoint
            queryset = DummyUser.objects.filter(organization_id=organization_id)
        elif organization_id:
            # Filter by organization_id if provided
            queryset = DummyUser.objects.filter(organization_id=organization_id)
        else:
            # Return all dummy users if no filter is provided
            queryset = DummyUser.objects.all()

        serializer = DummyUserSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new dummy user
        """
        serializer = DummyUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DummyUserByOrganizationView(APIView):
    """
    API View to get dummy users by organization ID
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get dummy users by organization ID
        """
        organization_id = request.query_params.get("organization_id")
        if not organization_id:
            return Response(
                {"error": "organization_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = DummyUser.objects.filter(organization_id=organization_id)
        serializer = DummyUserSerializer(queryset, many=True)
        return Response(serializer.data)
