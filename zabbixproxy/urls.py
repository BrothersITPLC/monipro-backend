from django.urls import path

from scripts.Test.views.send_sms import SendSMSView
from zabbixproxy.alert_functions import get_zabbix_alerts
from zabbixproxy.host_items_functions import get_host_items, get_real_time_data
from zabbixproxy.views import (  # ZabbixHostCreationView,
    AnsibleDeployView,
    CheckReachabilityView,
    GetZabbixHostes,
    HostAndUserGroupCreationView,
    HostAPIView,
    ZabbixUserCreationView,
)

urlpatterns = [
    path(
        "zabbix-users/", ZabbixUserCreationView.as_view(), name="zabbix-user-creation"
    ),
    # path(
    #     "zabbix-hosts/", ZabbixHostCreationView.as_view(), name="zabbix-host-creation"
    # ),
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
]
