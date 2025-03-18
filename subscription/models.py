from django.db import models


# Create your models here.
class PaymentPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.ForeignKey(
        "Price", on_delete=models.SET_NULL, null=True, related_name="payment_plans"
    )
    popular = models.BooleanField(default=False)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}-{self.price}"

    class Meta:
        verbose_name = "Payment Plan"
        verbose_name_plural = "Payment Plans"
        ordering = ["name"]


class Duration(models.Model):
    duration = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.duration

    class Meta:
        verbose_name = "Duration"
        verbose_name_plural = "Durations"
        ordering = ["duration"]


class Price(models.Model):
    duration = models.ForeignKey(
        Duration, on_delete=models.CASCADE, related_name="prices"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.duration.duration} - ${self.price}"

    class Meta:
        verbose_name = "Price"
        verbose_name_plural = "Prices"
        unique_together = ["duration", "price"]
        ordering = ["duration"]


class Feature(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Feature"
        verbose_name_plural = "Features"
        ordering = ["name"]


class PaymentPlanFeature(models.Model):
    payment_plan = models.ForeignKey(
        PaymentPlan, on_delete=models.CASCADE, related_name="features"
    )
    feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="payment_plans"
    )
    value = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment_plan.name} - {self.feature.name}: {self.value}"

    class Meta:
        verbose_name = "Payment Plan Feature"
        verbose_name_plural = "Payment Plan Features"
        unique_together = ["payment_plan", "feature"]
        ordering = ["payment_plan", "feature"]
