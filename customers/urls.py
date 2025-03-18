from django.urls import path

from .views import OrganizationInfoView

urlpatterns = [
    path("organization/", OrganizationInfoView.as_view(), name="organization-info"),
]
