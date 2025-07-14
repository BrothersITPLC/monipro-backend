from django.contrib import admin

from .models import (
    Host,
    HostCredentials,
    HostLifecycle,
    TaskStatus,
    TemplateGroupMirror,
    TemplateMirror,
    ZabbixAuthToken,
    ZabbixHost,
    ZabbixUser,
    ZabbixUserGroup,
)

# Register your models here.
admin.site.register(ZabbixUserGroup)
admin.site.register(ZabbixUser)
admin.site.register(ZabbixHost)
admin.site.register(TaskStatus)
admin.site.register(Host)
admin.site.register(HostCredentials)
admin.site.register(HostLifecycle)
admin.site.register(TemplateGroupMirror)
admin.site.register(TemplateMirror)
admin.site.register(ZabbixAuthToken)
