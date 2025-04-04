from django.urls import path

from zabbixproxy.views import (
    GetZabixHostes,
    ZabbixCredentialsCreationWrapper,
    ZabbixUserCreationView,
)
from zabbixproxy.views.host_items import get_host_items, get_real_time_data

urlpatterns = [
    path(
        "zabbix-users/", ZabbixUserCreationView.as_view(), name="zabbix-user-creation"
    ),
    path(
        "zabbix-credentials/",
        ZabbixCredentialsCreationWrapper.as_view(),
        name="zabbix-credentials-creation",
    ),
    path("hosts/", GetZabixHostes.as_view(), name="zabbix-hosts"),
    path("zabbix/host-items/", get_host_items, name="get_host_items"),
    path("zabbix/real-time-data/", get_real_time_data, name="get_real_time_data"),
]
