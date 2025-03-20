from django.urls import path

from .views import (
    NetworkDetailAPIView,
    NetworkListCreateAPIView,
    VMDetailAPIView,
    VMListCreateAPIView,
)

urlpatterns = [
    path("api/vms/", VMListCreateAPIView.as_view(), name="vm-list-create"),
    path("api/vms/<int:pk>/", VMDetailAPIView.as_view(), name="vm-detail"),
    path(
        "api/networks/", NetworkListCreateAPIView.as_view(), name="network-list-create"
    ),
    path(
        "api/networks/<int:pk>/", NetworkDetailAPIView.as_view(), name="network-detail"
    ),
]
