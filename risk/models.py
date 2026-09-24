from django.db import models

from companies.models import Company
from customers.models import Customer


class RiskScore(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
    )

    score = models.PositiveIntegerField()

    risk_level = models.CharField(
        max_length=20,
    )

    reasons = models.TextField(
        blank=True,
    )

    calculated_at = models.DateTimeField(
        auto_now=True,
    )

    def str(self):
        return f"{self.customer.name} - {self.score}"