from django.contrib import admin

from .models import Company, UserProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name")

    @admin.display(description="Company")
    def company_name(self, obj):
        return obj.company.name
