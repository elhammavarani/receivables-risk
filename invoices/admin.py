from django.contrib import admin

from .models import Invoice, Payment


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "customer_name",
        "company_name",
        "amount",
        "paid_amount",
        "remaining_amount_display",
        "invoice_date",
        "due_date",
    )

    @admin.display(description="Customer")
    def customer_name(self, obj):
        return obj.customer.name

    @admin.display(description="Company")
    def company_name(self, obj):
        return obj.company.name

    @admin.display(description="Remaining")
    def remaining_amount_display(self, obj):
        return obj.remaining_amount


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_name",
        "company_name",
        "amount",
        "payment_date",
    )

    @admin.display(description="Invoice")
    def invoice_name(self, obj):
        return obj.invoice.invoice_number

    @admin.display(description="Company")
    def company_name(self, obj):
        return obj.company.name