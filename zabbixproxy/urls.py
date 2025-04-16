from django.urls import path

from zabbixproxy.ansibal.views import AnsibleDeployView
from zabbixproxy.views.credentials.views import (
    HostAndUserGroupCreationView,
    ZabbixUserCreationView,
)
from zabbixproxy.views.host_items import get_host_items, get_real_time_data
from zabbixproxy.views.host_items.views import GetZabbixHostes, ZabbixHostCreationView

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
    path("zabbix/host-items/", get_host_items, name="get_host_items"),
    path("zabbix/real-time-data/", get_real_time_data, name="get_real_time_data"),
    path('deploy/', AnsibleDeployView.as_view(), name='deploy'),

]
