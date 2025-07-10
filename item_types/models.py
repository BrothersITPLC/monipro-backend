from django.db import models


class MonitoringCategoryAndItemType(models.Model):
    name = models.CharField(max_length=100)
    template = models.JSONField(default=list, blank=True)
    category_description = models.TextField()
    category_long_description = models.TextField()

    def __str__(self):
        return self.name
