from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import DummyUser
from ..serializers import DummyUserSerializer


class DummyUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DummyUser model to handle CRUD operations
    """

    serializer_class = DummyUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view returns a list of all dummy users for the currently authenticated user's organization
        or filters by organization_id if provided in query params
        """
        queryset = DummyUser.objects.all()
        organization_id = self.request.query_params.get("organization_id", None)

        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new dummy user
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def by_organization(self, request):
        """
        Custom endpoint to get dummy users by organization ID
        """
        organization_id = request.query_params.get("organization_id")
        if not organization_id:
            return Response(
                {"error": "organization_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = DummyUser.objects.filter(organization_id=organization_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
