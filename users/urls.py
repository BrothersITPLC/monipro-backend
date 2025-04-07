from django.urls import path

from .views import (
    ForgotPasswordView,
    GoogleExchangeView,
    Login,
    Logout,
    OrganizationInitialRegistrationView,
    PasswordResetView,
    PrivateInitialRegistrationView,
    TeamUserByOrganizationView,
    TeamUserView,
    UserProfileView,
    VerifyRegistrationOtp,
)

urlpatterns = [
    path(
        "organization-register/",
        OrganizationInitialRegistrationView.as_view(),
        name="organization-register",
    ),
    path(
        "private-register/",
        PrivateInitialRegistrationView.as_view(),
        name="private-register",
    ),
    path("verify/", VerifyRegistrationOtp.as_view(), name="verify"),
    path("login/", Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),
    path("users/", TeamUserView.as_view(), name="dummy-users"),
    path(
        "users/by-organization/",
        TeamUserByOrganizationView.as_view(),
        name="dummy-users-by-organization",
    ),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("password-forgot/", ForgotPasswordView.as_view(), name="password-forgot"),
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path("google-exchange/", GoogleExchangeView.as_view(), name="google-exchange"),
    path("auth/google/callback", GoogleExchangeView.as_view(), name="google-callback"),
]
