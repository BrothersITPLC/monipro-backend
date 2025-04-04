from django.urls import path

from zabbixproxy.views.credentials import (
    ZabbixCredentialsCreationWrapper,
    ZabbixHostCreationView,
    ZabbixUserCreationView,
)
from zabbixproxy.views.host_items import (
    GetZabbixHostes,
    get_host_items,
    get_real_time_data,
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
        ZabbixCredentialsCreationWrapper.as_view(),
        name="zabbix-credentials-creation",
    ),
    path("hosts/", GetZabbixHostes.as_view(), name="zabbix-hosts"),
    path("zabbix/host-items/", get_host_items, name="get_host_items"),
    path("zabbix/real-time-data/", get_real_time_data, name="get_real_time_data"),
]
