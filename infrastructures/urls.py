from django.urls import path

from .views import (
    NetworkDetailAPIView,
    NetworkListCreateAPIView,
    VMDetailAPIView,
    VMListCreateAPIView,
)

urlpatterns = [
    path("vms/", VMListCreateAPIView.as_view(), name="vm-list-create"),
    path("vms/<int:pk>/", VMDetailAPIView.as_view(), name="vm-detail"),
    path("networks/", NetworkListCreateAPIView.as_view(), name="network-list-create"),
    path("networks/<int:pk>/", NetworkDetailAPIView.as_view(), name="network-detail"),
]
