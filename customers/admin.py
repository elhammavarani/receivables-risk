from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "phone", "company_name")

    @admin.display(description="Company")
    def company_name(self, obj):
        return obj.company.name