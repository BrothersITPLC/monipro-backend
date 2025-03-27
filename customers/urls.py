from django.urls import path

from customers.views import (
    OrganizationInfoView,
    OrganizationPaymentUpdateView,
    PrivateInfoView,
)

urlpatterns = [
    path("organization/", OrganizationInfoView.as_view(), name="organization"),
    path("private/", PrivateInfoView.as_view(), name="private"),
    path(
        "organization/<int:pk>/update-payment/",
        OrganizationPaymentUpdateView.as_view(),
        name="organization-payment-update",
    ),
]
