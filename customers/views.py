from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from companies.models import UserProfile
from .models import Customer
from invoices.models import Invoice
from risk.models import RiskScore


@login_required
def customer_detail(request, customer_id):
    profile = UserProfile.objects.select_related(
        "company"
    ).filter(
        user=request.user
    ).first()

    if not profile:
        return render(
            request,
            "customers/detail.html",
            {
                "error": "شرکت برای کاربر تعریف نشده است.",
            },
        )

    customer = get_object_or_404(
        Customer,
        id=customer_id,
        company=profile.company,
    )

    invoices = Invoice.objects.filter(
        company=profile.company,
        customer=customer,
    ).order_by("-due_date")

    risk = RiskScore.objects.filter(
        company=profile.company,
        customer=customer,
    ).first()

    total_debt = sum(
        invoice.remaining_amount
        for invoice in invoices
    )

    open_invoice_count = sum(
        1
        for invoice in invoices
        if invoice.remaining_amount > 0
    )

    return render(
        request,
        "customers/detail.html",
        {
            "customer": customer,
            "invoices": invoices,
            "risk": risk,
            "total_debt": total_debt,
            "open_invoice_count": open_invoice_count,
        },
    )