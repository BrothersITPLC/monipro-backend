from django.urls import path

# from .views import (
#     SendPasswordResetEmailView,
#     UserChangePasswordView,
#     UserLoginView,
#     UserLogoutView,
#     UserPasswordResetView,
#     UserProfileView,
#     VerifyEmailView,
# )
from .views import OrganizationInitialRegistrationView

urlpatterns = [
    path("register/", OrganizationInitialRegistrationView.as_view(), name="register"),
    # path("verify/", VerifyEmailView.as_view(), name="verify"),
    # path("login/", UserLoginView.as_view(), name="login"),
    # path("profile/", UserProfileView.as_view(), name="profile"),
    # path("changepassword/", UserChangePasswordView.as_view(), name="changepassword"),
    # path(
    #     "send-reset-password-email/",
    #     SendPasswordResetEmailView.as_view(),
    #     name="send_reset_password_email",
    # ),
    # path(
    #     "reset-password/<uid>/<token>/",
    #     UserPasswordResetView.as_view(),
    #     name="reset_password",
    # ),
    # path("logout/", UserLogoutView.as_view(), name="logout"),
]
