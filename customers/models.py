from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone

from subscription.models import Duration, PaymentPlan, PaymentProvider


class OrganizationInfo(models.Model):
    organization_name = models.CharField(max_length=255)
    organization_phone = models.CharField(max_length=15, unique=True)
    organization_website = models.URLField(blank=True, null=True)
    organization_description = models.TextField(blank=True, null=True)
    payment_provider = models.ForeignKey(
        PaymentProvider, on_delete=models.PROTECT, blank=True, null=True
    )
    organization_payment_plan = models.ForeignKey(
        PaymentPlan, on_delete=models.PROTECT, null=True, blank=True
    )
    organization_payment_duration = models.ForeignKey(
        Duration, on_delete=models.PROTECT, null=True, blank=True
    )
    payment_start_date = models.DateField(default=timezone.now)
    payment_end_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.payment_start_date:
            self.payment_start_date = timezone.now().date()

        if self.organization_payment_duration:
            duration_mapping = {
                "monthly": relativedelta(months=1),
                "quarterly": relativedelta(months=3),
                "yearly": relativedelta(years=1),
            }
            delta = duration_mapping.get(
                self.organization_payment_duration.name.lower()
            )
            if delta:
                self.payment_end_date = self.payment_start_date + delta

        super().save(*args, **kwargs)

    def __str__(self):
        return self.organization_name
