from decimal import Decimal

from django import template

import jdatetime


register = template.Library()


@register.filter
def human_money(value):
    if value is None:
        return "-"

    try:
        value = Decimal(str(value))
    except (ValueError, TypeError):
        return value

    if abs(value) >= Decimal("1000000000"):
        number = value / Decimal("1000000000")
        text = f"{number:.2f}".rstrip("0").rstrip(".")
        return f"{text} میلیارد"

    if abs(value) >= Decimal("1000000"):
        number = value / Decimal("1000000")
        text = f"{number:.2f}".rstrip("0").rstrip(".")
        return f"{text} میلیون"

    if abs(value) >= Decimal("1000"):
        number = value / Decimal("1000")
        text = f"{number:.1f}".rstrip("0").rstrip(".")
        return f"{text} هزار"

    return f"{value:,.0f}"


@register.filter
def jalali_date(value):
    if not value:
        return "-"

    try:
        if hasattr(value, "date"):
            value = value.date()

        jalali = jdatetime.date.fromgregorian(
            date=value
        )

        return jalali.strftime("%Y/%m/%d")

    except (AttributeError, TypeError, ValueError):
        return value