from django.contrib import admin

from .models import ZabbixHost, ZabbixHostGroup, ZabbixUser, ZabbixUserGroup

# Register your models here.
admin.site.register(ZabbixHostGroup)
admin.site.register(ZabbixUserGroup)
admin.site.register(ZabbixUser)
admin.site.register(ZabbixHost)
