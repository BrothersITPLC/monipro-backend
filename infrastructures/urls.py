from django.urls import path

from .views import (
    NetworkDetailAPIView,
    NetworkInfoAPIView,
    NetworkListCreateAPIView,
    VMDetailAPIView,
    VMInfoAPIView,
    VMListCreateAPIView,
)

urlpatterns = [
    path("vms/", VMListCreateAPIView.as_view(), name="vm-list-create"),
    path("vms/<int:pk>/", VMDetailAPIView.as_view(), name="vm-detail"),
    path("networks/", NetworkListCreateAPIView.as_view(), name="network-list-create"),
    path("networks/<int:pk>/", NetworkDetailAPIView.as_view(), name="network-detail"),
    path("vm-info/", VMInfoAPIView.as_view(), name="vm-info"),
    path("networks-info/", NetworkInfoAPIView.as_view(), name="networks-info"),
]
