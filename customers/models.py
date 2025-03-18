from django.db import models

from subscription.models import PaymentPlan


class OrganizationInfo(models.Model):
    organization_name = models.CharField(max_length=255, unique=True)
    organization_phone = models.CharField(max_length=15)
    organization_website = models.URLField(blank=True, null=True)
    organization_description = models.TextField(blank=True, null=True)
    organization_payment_plane = models.ForeignKey(
        PaymentPlan, on_delete=models.PROTECT, blank=True, null=True
    )

    def __str__(self):
        return self.organization_name
