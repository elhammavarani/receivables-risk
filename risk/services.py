from django.utils import timezone

from invoices.models import Invoice
from risk.models import RiskScore
from risk.risk_engine import calculate_risk


def calculate_company_risks(company):
    today = timezone.localdate()

    invoices = Invoice.objects.filter(
        company=company,
    ).select_related("customer")

    for invoice in invoices:
        overdue_days = max(
            (today - invoice.due_date).days,
            0,
        )

        result = calculate_risk(
            overdue_days,
            invoice.remaining_amount,
        )

        RiskScore.objects.update_or_create(
            company=invoice.company,
            customer=invoice.customer,
            defaults={
                "score": result["score"],
                "risk_level": result["level"],
                "reasons": "، ".join(result["reasons"]),
            },
        )