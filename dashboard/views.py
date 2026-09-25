from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companies.models import UserProfile
from .services import (
    get_dashboard_summary,
    get_high_risk_customers,
    get_today_actions,
)


@login_required
def dashboard_home(request):
    profile = UserProfile.objects.select_related(
        "company"
    ).filter(
        user=request.user
    ).first()

    if not profile:
        return render(
            request,
            "dashboard/home.html",
            {
                "error": "شرکت برای کاربر تعریف نشده است.",
            },
        )

    summary = get_dashboard_summary(
        profile.company
    )

    high_risk_customers = get_high_risk_customers(
        profile.company
    )

    today_actions = get_today_actions(
        profile.company
    )

    return render(
        request,
        "dashboard/home.html",
        {
            **summary,
            "high_risk_customers": high_risk_customers,
            "today_actions": today_actions,
        },
    )