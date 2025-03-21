from django.urls import path

from subscription.views import PaymentPlanListView

urlpatterns = [
    path("plans/", PaymentPlanListView.as_view(), name="payment-plan-list"),
]
