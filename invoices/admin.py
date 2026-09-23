from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "customer_name",
        "company_name",
        "amount",
        "paid_amount",
        "invoice_date",
        "due_date",
    )

    @admin.display(description="Customer")
    def customer_name(self, obj):
        return obj.customer.name

    @admin.display(description="Company")
    def company_name(self, obj):
        return obj.company.name

