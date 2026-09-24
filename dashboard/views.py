from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_home(request):
    context = {
        "total_receivables": 0,
        "total_overdue": 0,
        "overdue_invoice_count": 0,
    }

    return render(
        request,
        "dashboard/home.html",
        context,
    )
