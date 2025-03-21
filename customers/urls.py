from django.urls import path

from customers.views import OrganizationInfoView, OrganizationPaymentUpdateView

urlpatterns = [
    path("organization/", OrganizationInfoView.as_view(), name="organization"),
    path(
        "organization/<int:pk>/update-payment/",
        OrganizationPaymentUpdateView.as_view(),
        name="organization-payment-update",
    ),
]
