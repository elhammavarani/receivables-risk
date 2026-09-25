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