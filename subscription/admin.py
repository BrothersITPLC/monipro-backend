from django.contrib import admin

from .models import Duration, Feature, PaymentPlan, PaymentPlanFeature, Price

# Register your models here.
admin.site.register(PaymentPlan)
admin.site.register(PaymentPlanFeature)
admin.site.register(Feature)
admin.site.register(Duration)
admin.site.register(Price)
