from django.urls import path

from subscription.views import PaymentPlanListView, PaymentProviderView

urlpatterns = [
    path("plans/", PaymentPlanListView.as_view(), name="payment-plan-list"),
    path("providers/", PaymentProviderView.as_view(), name="payment-provider-list"),
]
