from django.urls import path

from .views import (
    Login,
    Logout,
    OrganizationInitialRegistrationView,
    TeamUserByOrganizationView,
    TeamUserView,
    UserProfileView,
    VerifyRegistrationOtp,
)

urlpatterns = [
    path("register/", OrganizationInitialRegistrationView.as_view(), name="register"),
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
]
