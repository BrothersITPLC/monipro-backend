from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="monipro API",
        default_version="v1",
        description="Description of your API",
    ),
    url="http://localhost:8000/",  # Add this line to set the base URL
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("api/", include("users.urls")),
    path("api/", include("subscription.urls")),
    path("api/", include("customers.urls")),
    path("api/", include("infrastructures.urls")),
]
