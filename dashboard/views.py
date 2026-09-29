from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companies.models import UserProfile
from invoices.models import Invoice

from .services import (
    get_dashboard_summary,
    get_high_risk_customers,
    get_today_actions,
)


@login_required
def dashboard_home(request):
    profile = (
        UserProfile.objects
        .select_related("company")
        .filter(user=request.user)
        .first()
    )

    if not profile:
        return render(
            request,
            "dashboard/home.html",
            {
                "error": "شرکت برای کاربر تعریف نشده است.",
                "has_data": False,
            },
        )

    company = profile.company

    # بررسی می‌کنیم آیا این شرکت اصلاً فاکتوری وارد کرده است یا نه
    has_data = Invoice.objects.filter(
        company=company
    ).exists()

    # اگر هنوز هیچ اطلاعاتی وارد نشده،
    # داشبورد آماری را اجرا نکن
    if not has_data:
        return render(
            request,
            "dashboard/home.html",
            {
                "has_data": False,
            },
        )

    summary = get_dashboard_summary(company)

    high_risk_customers = get_high_risk_customers(company)

    today_actions = get_today_actions(company)

    return render(
        request,
        "dashboard/home.html",
        {
            **summary,
            "has_data": True,
            "high_risk_customers": high_risk_customers,
            "today_actions": today_actions,
        },
    )