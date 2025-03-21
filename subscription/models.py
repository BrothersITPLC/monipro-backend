from django.db import models


class PaymentProvider(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Payment Provider"
        verbose_name_plural = "Payment Providers"
        ordering = ["name"]


class Duration(models.Model):
    DURATION_CHOICES = [
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]
    name = models.CharField(max_length=20, choices=DURATION_CHOICES)

    def __str__(self):
        return f"{self.name} "

    class Meta:
        verbose_name = "Duration"
        verbose_name_plural = "Durations"
        ordering = ["name"]


class PaymentPlan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    popular = models.BooleanField(default=False)
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Payment Plan"
        verbose_name_plural = "Payment Plans"
        ordering = ["name"]


class PaymentPlanDuration(models.Model):
    payment_plan = models.ForeignKey(
        "PaymentPlan", on_delete=models.PROTECT, related_name="durations"
    )
    duration = models.ForeignKey(Duration, on_delete=models.PROTECT)
    deduction_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.payment_plan.name} - {self.duration.name} - (-{self.deduction_percentage}%)"


class Feature(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Feature"
        verbose_name_plural = "Features"
        ordering = ["name"]


class FeatureValue(models.Model):
    feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="values"
    )
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.feature.name}: {self.value}"

    class Meta:
        verbose_name = "Feature Value"
        verbose_name_plural = "Feature Values"
        unique_together = [("feature", "value")]
        ordering = ["feature", "value"]


class PaymentPlanFeature(models.Model):
    payment_plan = models.ForeignKey(
        PaymentPlan, on_delete=models.CASCADE, related_name="plan_features"
    )
    feature_value = models.ForeignKey(FeatureValue, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.payment_plan.name} - {self.feature_value.feature.name}: {self.feature_value.value}"

    class Meta:
        verbose_name = "Payment Plan Feature"
        verbose_name_plural = "Payment Plan Features"
        ordering = [
            "payment_plan",
        ]
