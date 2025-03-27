from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructures.models import VM, Network
from infrastructures.serializers import (
    NetworkListSerializer,
    VMListSerializer,
)


class InfrastructureListView(APIView):
    def get(self, request):
        user = request.user

        vms = VM.objects.filter(belong_to=user)
        networks = Network.objects.filter(belong_to=user)

        vm_serializer = VMListSerializer(vms, many=True)
        network_serializer = NetworkListSerializer(networks, many=True)

        return Response(
            {"vms": vm_serializer.data, "networks": network_serializer.data}
        )
