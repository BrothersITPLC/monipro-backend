from django.urls import path

from customers.views import OrganizationInfoView

urlpatterns = [
    path("organization/", OrganizationInfoView.as_view(), name="organization"),
]
