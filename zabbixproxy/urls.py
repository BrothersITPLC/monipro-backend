from django.urls import path

from scripts.views.send_sms import SendSMSView
from zabbixproxy.functions.alert_functions import get_zabbix_alerts
from zabbixproxy.functions.host_items_functions import (
    get_host_items,
    get_real_time_data,
)
from zabbixproxy.views import (
    AnsibleDeployView,
    CheckReachabilityView,
    GetTemplateNameView,
    GetTemplates,
    GetZabbixHostes,
    HostAndUserGroupCreationView,
    HostAPIView,
    HostDeletionView,
    HostVisualizationsView,
    TemplateGroupView,
    TemplateView,
    ZabbixHostCreationView,
    ZabbixUserCreationView,
)

urlpatterns = [
    path(
        "zabbix-users/", ZabbixUserCreationView.as_view(), name="zabbix-user-creation"
    ),
    path(
        "zabbix-credentials/",
        HostAndUserGroupCreationView.as_view(),
        name="zabbix-credentials-creation",
    ),
    path("hosts/", GetZabbixHostes.as_view(), name="zabbix-hosts"),
    path("host-items/", get_host_items, name="get_host_items"),
    path("real-time-data/", get_real_time_data, name="get_real_time_data"),
    path("deploy/", AnsibleDeployView.as_view(), name="deploy"),
    path("get-zabbix-alerts/", get_zabbix_alerts, name="get-zabbix-alerts"),
    path("local-hosts/", HostAPIView.as_view(), name="local-host-list-create"),
    path("local-hosts/<int:pk>/", HostAPIView.as_view(), name="local-host-detail"),
    path("send-sms/", SendSMSView.as_view(), name="send-sms"),
    path("reachability/", CheckReachabilityView.as_view(), name="reachability"),
    path(
        "post-host-creation/",
        ZabbixHostCreationView.as_view(),
        name="post_host_creation",
    ),
    path("template-name/", GetTemplateNameView.as_view(), name="template-name"),
    path("templates/", GetTemplates.as_view(), name="templates"),
    path("delete-host/", HostDeletionView.as_view(), name="host-deletion"),
    path(
        "create-template-group/",
        TemplateGroupView.as_view(),
        name="create-template-group",
    ),
    path("create-template/", TemplateView.as_view(), name="create-template"),
    path(
        "visualizations/<str:host_id>/",
        HostVisualizationsView.as_view(),
        name="host-visualizations",
    ),
]
