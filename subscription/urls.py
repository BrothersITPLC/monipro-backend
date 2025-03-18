from django.urls import path

from .views import PaymentPlanListView

urlpatterns = [
    path("plans/", PaymentPlanListView.as_view(), name="payment-plan-list"),
]
