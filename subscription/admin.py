from django.contrib import admin

from .models import (
    Duration,
    Feature,
    FeatureValue,
    PaymentPlan,
    PaymentPlanDuration,
    PaymentPlanFeature,
    PaymentProvider,
)

# Register your models here.
admin.site.register(PaymentPlan)
admin.site.register(PaymentPlanFeature)
admin.site.register(Feature)
admin.site.register(Duration)
admin.site.register(FeatureValue)
admin.site.register(PaymentProvider)
admin.site.register(PaymentPlanDuration)
