# urls.py

from django.urls import path

from agents.views import AlertInsightAPIView

urlpatterns = [
    path(
        "get-ai-explanation/", AlertInsightAPIView.as_view(), name="get-ai-explanation"
    ),
]
