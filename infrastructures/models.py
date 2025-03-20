from django.db import models

from users.models import User

NETWORK_TYPE_CHOICES = [
    ("private", "Private"),
    ("public", "Public"),
]


class VM(models.Model):
    domainName = models.CharField(max_length=255)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    ipAddress = models.GenericIPAddressField()
    networkType = models.CharField(max_length=7, choices=NETWORK_TYPE_CHOICES)
    belong_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vms")

    def __str__(self):
        return f"{self.domainName} ({self.ipAddress})"


class Network(models.Model):
    DEVICE_TYPE_CHOICES = [
        ("router", "Router"),
        ("firewall", "Firewall"),
        ("switch", "Switch"),
        ("load_balancer", "Load Balancer"),
    ]
    networkType = models.CharField(max_length=7, choices=NETWORK_TYPE_CHOICES)
    deviceType = models.CharField(max_length=15, choices=DEVICE_TYPE_CHOICES)
    ipAddress = models.GenericIPAddressField()
    subnetMask = models.CharField(max_length=15)
    gateway = models.GenericIPAddressField()
    name = models.CharField(max_length=255)
    belong_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="networks"
    )

    def __str__(self):
        return f"{self.name} ({self.ipAddress}-{self.deviceType})"
