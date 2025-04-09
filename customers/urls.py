from django.urls import path

from customers.views import OrganizationInfoCreateView, OrganizationPaymentUpdateView

urlpatterns = [
    path("organization/", OrganizationInfoCreateView.as_view(), name="organization"),
    path(
        "organization/<int:pk>/update-payment/",
        OrganizationPaymentUpdateView.as_view(),
        name="organization-payment-update",
    ),
]
