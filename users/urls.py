from django.urls import path

from .views import (
    AddUserView,
    ChangePasswordView,
    ForgotPasswordView,
    GetTeamUsersView,
    GoogleExchangeView,
    InitialRegistrationView,
    Login,
    Logout,
    PasswordResetView,
    ProfilePictureUpdateView,
    SetUserActiveAPIView,
    TeamUserByOrganizationView,
    TeamUserView,
    UpdateProfileView,
    UserProfileView,
    VerifyRegistrationOtp,
    TelegramAuthView
)
from .views.csrf import get_csrf_token


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
    path("telegram/", TelegramAuthView.as_view(), name="telegram_auth"),
    path(
        "update-profile-picture/",
        ProfilePictureUpdateView.as_view(),
        name="update-profile-picture",
    ),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("update-profile/", UpdateProfileView.as_view(), name="update-profile"),
    path("add-team-user/", AddUserView.as_view(), name="add-team-user"),
    path("get-team-users/", GetTeamUsersView.as_view(), name="get-team-users"),
    path("set-active/", SetUserActiveAPIView.as_view(), name="set-user-active"),
    path('csrf/', get_csrf_token, name='get_csrf_token'),
    path('register/', InitialRegistrationView.as_view(), name='register'),
]
from users.views.login import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns += [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
