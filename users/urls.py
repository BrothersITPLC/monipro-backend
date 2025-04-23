from django.urls import path

from .views import (
    ChangePasswordView,
    ForgotPasswordView,
    GoogleExchangeView,
    InitialRegistrationView,
    Login,
    Logout,
    PasswordResetView,
    ProfilePictureUpdateView,
    TeamUserByOrganizationView,
    TeamUserView,
    UpdateProfileView,
    UserProfileView,
    VerifyRegistrationOtp,
)

urlpatterns = [
    path(
        "initial-register/",
        InitialRegistrationView.as_view(),
        name="initial-register",
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
    path(
        "update-profile-picture/",
        ProfilePictureUpdateView.as_view(),
        name="update-profile-picture",
    ),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("update-profile/", UpdateProfileView.as_view(), name="update-profile"),
]
