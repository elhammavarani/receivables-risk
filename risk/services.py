from django.utils import timezone

from invoices.models import Invoice
from risk.models import RiskScore
from risk.risk_engine import calculate_risk


def calculate_company_risks(company):
    today = timezone.localdate()

    invoices = (
        Invoice.objects
        .filter(company=company)
        .select_related("customer")
    )

    customer_data = {}

    for invoice in invoices:
        if invoice.customer_id not in customer_data:
            customer_data[invoice.customer_id] = {
                "customer": invoice.customer,
                "max_overdue_days": 0,
                "total_debt": 0,
            }

        data = customer_data[invoice.customer_id]

        overdue_days = max(
            (today - invoice.due_date).days,
            0,
        )

        remaining_amount = invoice.remaining_amount

        data["max_overdue_days"] = max(
            data["max_overdue_days"],
            overdue_days,
        )

        if remaining_amount > 0:
            data["total_debt"] += remaining_amount

    for data in customer_data.values():
        customer = data["customer"]

        result = calculate_risk(
            data["max_overdue_days"],
            data["total_debt"],
        )

        RiskScore.objects.update_or_create(
            company=company,
            customer=customer,
            defaults={
                "score": result["score"],
                "risk_level": result["level"],
                "reasons": "، ".join(result["reasons"]),
            },
        )