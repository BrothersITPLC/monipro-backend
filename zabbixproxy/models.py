from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ZabbixHostGroup(models.Model):
    hostgroupid = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}-{self.hostgroupid}"


class ZabbixUserGroup(models.Model):
    PERMISSION_CHOICES = [
        ("denied", 0),
        ("read-only", 2),
        ("read-write", 3),
    ]
    usergroupid = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    hostgroupid = models.ForeignKey(ZabbixHostGroup, on_delete=models.CASCADE)
    permission = models.CharField(max_length=15, choices=PERMISSION_CHOICES)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}-{self.usergroupid}"


class ZabbixUser(models.Model):
    PERMISSION_CHOICES = [
        ("user", 0),
        ("admin", 1),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    userid = models.CharField(max_length=50, null=True, blank=True)
    user_group = models.ForeignKey(ZabbixUserGroup, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    roleid = models.CharField(max_length=50, choices=PERMISSION_CHOICES)

    def __str__(self):
        return f"{self.username}-{self.userid}"


class ZabbixHost(models.Model):
    hostgroup = models.ForeignKey(ZabbixHostGroup, on_delete=models.CASCADE)
    hostid = models.CharField(max_length=50, null=True, blank=True)
    host = models.CharField(max_length=50, null=True, blank=True)
    ip = models.CharField(max_length=50, null=True, blank=True)
    dns = models.CharField(max_length=50, null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.host}-{self.hostid}"
