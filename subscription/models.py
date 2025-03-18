from django.db import models


class Duration(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Duration"
        verbose_name_plural = "Durations"
        ordering = ["name"]


class Price(models.Model):
    duration = models.ForeignKey(
        Duration, on_delete=models.CASCADE, related_name="prices"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.duration} - ${self.amount}"

    class Meta:
        verbose_name = "Price"
        verbose_name_plural = "Prices"
        unique_together = [("duration", "amount")]
        ordering = ["duration"]


class PaymentPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.ForeignKey(
        Price, on_delete=models.SET_NULL, null=True, related_name="payment_plans"
    )
    popular = models.BooleanField(default=False)
    description = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.price}"

    class Meta:
        verbose_name = "Payment Plan"
        verbose_name_plural = "Payment Plans"
        ordering = ["name"]


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
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    feature_value = models.ForeignKey(FeatureValue, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.payment_plan.name} - {self.feature.name}: {self.feature_value.value}"

    class Meta:
        verbose_name = "Payment Plan Feature"
        verbose_name_plural = "Payment Plan Features"
        ordering = ["payment_plan", "feature"]


class PaymentProvider(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Payment Provider"
        verbose_name_plural = "Payment Providers"
        ordering = ["name"]
