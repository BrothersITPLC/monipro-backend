import random
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        name,
        password=None,
        password2=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("User must have an email address")
        if password != password2:
            raise ValueError("Passwords don't match")
        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        # Update the method signature
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(
            email,
            name,
            password,
            password2=password,
            **extra_fields,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    name = models.CharField(verbose_name="user name", max_length=200, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(
        verbose_name="First name", max_length=100, blank=True, null=True
    )
    last_name = models.CharField(
        verbose_name="Last name", max_length=100, blank=True, null=True
    )
    is_organization = models.BooleanField(default=False)
    is_organization_completed_information = models.BooleanField(default=False)
    organization = models.ForeignKey(
        "customers.OrganizationInfo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members",
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self.is_admin = value

    @property
    def is_superuser(self):
        return self.is_admin

    @is_superuser.setter
    def is_superuser(self, value):
        self.is_admin = value


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "otp_code")

    def save(self, *args, **kwargs):
        if not self.pk:
            # Set expiration time (e.g. 10 minutes from creation)
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if the OTP is still valid and has not been used."""
        return (not self.is_used) and (timezone.now() < self.expires_at)

    def __str__(self):
        return f"OTP for {self.user.email}: {self.otp_code}"


def generate_otp():
    """Generate a random 6-digit OTP code."""
    return "{:06d}".format(random.randint(0, 999999))


def generate_unique_otp(user=None):
    """Generate a unique OTP code."""
    while True:
        otp_code = "".join(str(random.randint(0, 9)) for _ in range(6))
        if user is None:
            if not OTP.objects.filter(otp_code=otp_code).exists():
                return otp_code
        else:
            if not OTP.objects.filter(user=user, otp_code=otp_code).exists():
                return otp_code
    max_attempts = 5
    for _ in range(max_attempts):
        otp_code = generate_otp()
        if not OTP.objects.filter(user=user, otp_code=otp_code, is_used=False).exists():
            return otp_code
    raise Exception("Could not generate a unique OTP. Try again later.")


class RegistrationAttempt(models.Model):
    email = models.EmailField()
    attempt_time = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)

    def __str__(self):
        return f"Registration attempt for {self.email} at {self.attempt_time}"


class DummyUser(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    organization = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="dummy_users"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
