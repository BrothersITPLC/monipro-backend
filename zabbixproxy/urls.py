from django.urls import path

from zabbixproxy.host_items_functions import get_host_items, get_real_time_data
from zabbixproxy.views import (
    AnsibleDeployView,
    GetZabbixHostes,
    HostAndUserGroupCreationView,
    ZabbixHostCreationView,
    ZabbixUserCreationView,
)

urlpatterns = [
    path(
        "zabbix-users/", ZabbixUserCreationView.as_view(), name="zabbix-user-creation"
    ),
    path(
        "zabbix-hosts/", ZabbixHostCreationView.as_view(), name="zabbix-host-creation"
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
]
