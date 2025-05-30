from django.urls import path

from item_types.views import (
    AgentMonitoringItemTypesListView,
    MonitoringCategoryListView,
    SimpleCheckItemTypesListView,
)

urlpatterns = [
    path(
        "simple-check-item-list/",
        SimpleCheckItemTypesListView.as_view(),
        name="simple-check-item-list",
    ),
    path(
        "monitoring-category-list/",
        MonitoringCategoryListView.as_view(),
        name="monitoring-category-list",
    ),
    path(
        "agent-monitoring-item-list/",
        AgentMonitoringItemTypesListView.as_view(),
        name="agent-monitoring-item-list",
    ),
]
