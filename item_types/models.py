from django.db import models


class SimpleCheckItemTypes(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class AgentMonitoringItemType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class MonitoringCategory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    long_description = models.TextField()

    def __str__(self):
        return self.title
