from uuid import uuid4

from django.db import models

from customers.models import OrganizationInfo


class Status(models.TextChoices):
    CREATED = "created", "CREATED"
    PENDING = "pending", "PENDING"
    SUCCESS = "success", "SUCCESS"
    FAILED = "failed", "FAILED"


class TransactionMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.CREATED
    )
    customer = models.ForeignKey(
        OrganizationInfo,
        on_delete=models.CASCADE,
        related_name="payment_transaction",
        null=True,
        blank=True,
    )
    response_dump = models.JSONField(default=dict, blank=True)
    checkout_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"ChapaTransaction {self.id} - {self.status}"


class Transaction(TransactionMixin):
    pass
