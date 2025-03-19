from django.urls import path

from .views import (
    DummyUserByOrganizationView,
    DummyUserView,
    Login,
    Logout,
    OrganizationInitialRegistrationView,
    VerifyRegistrationOtp,
)

urlpatterns = [
    path("register/", OrganizationInitialRegistrationView.as_view(), name="register"),
    path("verify/", VerifyRegistrationOtp.as_view(), name="verify"),
    path("login/", Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),
    path("users/", DummyUserView.as_view(), name="dummy-users"),
    path(
        "users/by-organization/",
        DummyUserByOrganizationView.as_view(),
        name="dummy-users-by-organization",
    ),
]
