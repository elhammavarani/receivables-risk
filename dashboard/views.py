from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companies.models import UserProfile
from .services import get_dashboard_summary


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

    return render(
        request,
        "dashboard/home.html",
        summary,
    )