from django.contrib import admin

from .models import OTP, RegistrationAttempt, User

# Register your models here.
admin.site.register(User)
admin.site.register(RegistrationAttempt)
admin.site.register(OTP)
