import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from customers.models import OrganizationInfo

User = get_user_model()


class ZabbixHostGroup(models.Model):
    hostgroupid = models.CharField(max_length=50, null=True, blank=True)
    belongs_to = models.ForeignKey(
        OrganizationInfo,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="organization_hostgroup",
    )
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
    roleid = models.IntegerField(choices=PERMISSION_CHOICES)

    def __str__(self):
        return f"{self.username}-{self.userid}"


class ZabbixHost(models.Model):
    hostgroup = models.ForeignKey(ZabbixHostGroup, on_delete=models.CASCADE)
    hostid = models.IntegerField()
    host = models.CharField(max_length=50, unique=True)
    ip = models.CharField(max_length=50, null=True, blank=True, unique=True)
    dns = models.CharField(max_length=50, null=True, blank=True, default="")
    port = models.IntegerField(default=10050)
    device_type = models.CharField(max_length=50, null=True, blank=True)
    network_device_type = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.host}-{self.hostid}"


class ZabbixAuthToken(models.Model):
    auth = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_or_create_token(cls, auth_value):
        cls.objects.all().delete()
        return cls.objects.create(auth=auth_value)

    def __str__(self):
        return self.auth


# class ZabbixAuthToken(models.Model):
#     auth = models.CharField(max_length=100, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE)

#     @classmethod
#     def get_or_create_token(cls, auth_value):
#         cls.objects.all().delete()
#         return cls.objects.create(auth=auth_value)

#     def __str__(self):
#         return self.auth


class TaskStatus(models.Model):
    """Model to track the status of asynchronous tasks"""

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    task_id = models.CharField(max_length=255, unique=True)
    task_type = models.CharField(max_length=100)
    parent_task = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    host_ip = models.CharField(max_length=50, null=True, blank=True)
    dns = models.CharField(max_length=50, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    successfully_executed_tasks = models.JSONField(null=True, blank=True)
    unsuccessfully_executed_tasks = models.JSONField(null=True, blank=True)
    faild_task = models.IntegerField(default=0)
    successful_task = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task_type} - {self.status} ({self.task_id})"

    def update_status(
        self,
        status,
        successfully_executed_tasks=None,
        error_message=None,
        unsuccessfully_executed_tasks=None,
        faild_task=None,
        successful_task=None,
    ):
        self.status = status
        if successfully_executed_tasks:
            self.successfully_executed_tasks = successfully_executed_tasks
        if unsuccessfully_executed_tasks:
            self.unsuccessfully_executed_tasks = unsuccessfully_executed_tasks
        if faild_task:
            self.faild_task = faild_task
        if successful_task:
            self.successful_task = successful_task
        if error_message:
            self.error_message = error_message
        self.updated_at = timezone.now()
        self.save()


class HostForReachabilityMonitoring(models.Model):
    host = models.ForeignKey(ZabbixHost, on_delete=models.CASCADE)
    host_ip = models.CharField(max_length=50, null=True, blank=True)
    dns = models.CharField(max_length=50, null=True, blank=True)
    hostgroup = models.ForeignKey(ZabbixHostGroup, on_delete=models.CASCADE)
    hostid = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.host}-{self.hostid}"


class MonitoringType(models.TextChoices):
    SIMPLE_CHECKS = (
        "simple_checks",
        "Simple Checks – Basic Network and Service Availability Checks",
    )
    AGENT = "agent", "Agent – Advanced Agent-Based Monitoring (Zabbix Agent2)"
    SNMP = (
        "snmp",
        "SNMP – Network Device Monitoring via SNMP (Simple Network Management Protocol)",
    )
    IPMI = (
        "ipmi",
        "IPMI – Hardware-Level Monitoring via IPMI (Intelligent Platform Management Interface)",
    )
    APPLICATION_LEVEL = (
        "application_level",
        "Application Level – Application-Specific Monitoring (e.g., Databases, Web Apps, Services)",
    )


class zabbbixTemplate(models.Model):
    templateid = models.CharField(max_length=50, null=True, blank=True)
    template_name = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    monitoring_type = models.CharField(
        max_length=32,
        choices=MonitoringType.choices,
        default=MonitoringType.SIMPLE_CHECKS,
    )

    def __str__(self):
        return f"{self.template_name}-{self.templateid}"


class Host(models.Model):
    DEVICE_TYPE_CHOICES = (
        ("vm", "vm"),
        ("network", "network"),
    )
    NETWORK_DEVICE_TYPE = (
        ("switch", "switch"),
        ("router", "router"),
        ("firewall", "firewall"),
        ("load_balancer", "load_balancer"),
    )
    host = models.CharField(max_length=255, unique=True)
    ip = models.CharField(max_length=100, null=True, blank=True)
    dns = models.CharField(max_length=100, null=True, blank=True)
    host_group = models.ForeignKey(
        ZabbixHostGroup, on_delete=models.CASCADE, null=True, blank=True
    )
    device_type = models.CharField(
        max_length=50, choices=DEVICE_TYPE_CHOICES, default="vm"
    )
    network_device_type = models.CharField(
        max_length=50, choices=NETWORK_DEVICE_TYPE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.host_name}-{self.host_ip}"


class HostCredentials(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.host.host}"
