from datetime import date

from invoices.models import Invoice
from risk.models import RiskScore


def get_dashboard_summary(company):
    invoices = Invoice.objects.filter(
        company=company,
    )

    total_receivables = sum(
        invoice.remaining_amount
        for invoice in invoices
    )

    total_overdue = sum(
        invoice.remaining_amount
        for invoice in invoices
        if invoice.remaining_amount > 0
        and invoice.due_date < date.today()
    )

    overdue_invoice_count = sum(
        1
        for invoice in invoices
        if invoice.remaining_amount > 0
        and invoice.due_date < date.today()
    )

    risk_scores = RiskScore.objects.filter(
        company=company,
    )

    high_risk_customer_count = (
        risk_scores
        .filter(score__gte=61)
        .values("customer")
        .distinct()
        .count()
    )

    overdue_percentage = 0

    if total_receivables > 0:
        overdue_percentage = (
            total_overdue / total_receivables
        ) * 100

    return {
        "total_receivables": total_receivables,
        "total_overdue": total_overdue,
        "overdue_invoice_count": overdue_invoice_count,
        "high_risk_customer_count": high_risk_customer_count,
        "overdue_percentage": overdue_percentage,
    }


def get_high_risk_customers(company):
    risk_scores = (
        RiskScore.objects
        .filter(
            company=company,
            score__gte=61,
        )
        .select_related("customer")
        .order_by("-score")
    )

    return risk_scores


def get_overdue_invoices(company):
    invoices = (
        Invoice.objects
        .filter(
            company=company,
        )
        .select_related("customer")
        .order_by("-due_date")
    )

    overdue_invoices = [
        invoice
        for invoice in invoices
        if invoice.remaining_amount > 0
        and invoice.due_date < date.today()
    ]

    return overdue_invoices


def get_today_actions(company):
    invoices = (
        Invoice.objects
        .filter(
            company=company,
            due_date__lt=date.today(),
        )
        .select_related("customer")
    )

    customer_actions = {}

    for invoice in invoices:

        if invoice.remaining_amount <= 0:
            continue

        customer_id = invoice.customer.id

        if customer_id not in customer_actions:
            customer_actions[customer_id] = {
                "customer": invoice.customer,
                "total_overdue_amount": invoice.remaining_amount,
                "overdue_days": (
                    date.today() - invoice.due_date
                ).days,
            }

        else:
            customer_actions[customer_id][
                "total_overdue_amount"
            ] += invoice.remaining_amount

            overdue_days = (
                date.today() - invoice.due_date
            ).days

            if overdue_days > customer_actions[customer_id][
                "overdue_days"
            ]:
                customer_actions[customer_id][
                    "overdue_days"
                ] = overdue_days

    actions = []

    for customer_data in customer_actions.values():

        customer = customer_data["customer"]

        risk = RiskScore.objects.filter(
            company=company,
            customer=customer,
        ).first()

        risk_score = risk.score if risk else 0

        priority = (
            risk_score
            * float(customer_data["total_overdue_amount"])
        )

        actions.append(
            {
                "customer": customer,
                "total_overdue_amount": customer_data[
                    "total_overdue_amount"
                ],
                "overdue_days": customer_data[
                    "overdue_days"
                ],
                "risk_score": risk_score,
                "priority": priority,
            }
        )

    actions.sort(
        key=lambda item: item["priority"],
        reverse=True,
    )

    return actions