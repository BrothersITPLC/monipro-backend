from django.urls import path

from item_types.views import MonitoringCategoryAndItemTypetView

urlpatterns = [
    path(
        "monitoring-category-templates/",
        MonitoringCategoryAndItemTypetView.as_view(),
        name="monitoring_category_templates",
    )
]
