from django.db import models

from companies.models import Company
from customers.models import Customer


class Invoice(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    invoice_number = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    paid_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )

    invoice_date = models.DateField()
    due_date = models.DateField()
    last_payment_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number

    @property
    def remaining_amount(self):
        return self.amount - self.paid_amount
    


class Payment(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=18, decimal_places=2)
    payment_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.amount}"


    