from django.urls import path

from payment.views import ChapaPaymentInitialization, ChapaPaymenVerificationView

urlpatterns = [
    path(
        "payment/chapa-initialize/",
        ChapaPaymentInitialization.as_view(),
        name="chapa_payment_initialization",
    ),
    path(
        "payment/chapa-verify/",
        ChapaPaymenVerificationView.as_view(),
        name="chapa_payment_verification",
    ),
]
