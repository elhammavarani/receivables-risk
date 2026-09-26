def calculate_risk_score(
    overdue_days,
    debt_amount,
):
    score = 0

    # مدت تأخیر
    if overdue_days >= 90:
        score += 50
    elif overdue_days >= 60:
        score += 40
    elif overdue_days >= 30:
        score += 25
    elif overdue_days > 0:
        score += 10

    # مبلغ بدهی
    if debt_amount >= 500_000_000:
        score += 50
    elif debt_amount >= 200_000_000:
        score += 40
    elif debt_amount >= 100_000_000:
        score += 25
    elif debt_amount > 0:
        score += 10

    return min(score, 100)


def get_risk_level(score):
    if score >= 81:
        return "Critical"
    elif score >= 61:
        return "High"
    elif score >= 31:
        return "Medium"
    return "Low"


def get_risk_reasons(
    overdue_days,
    debt_amount,
):
    reasons = []

    if overdue_days >= 90:
        reasons.append(
            f"{overdue_days} روز تأخیر"
        )
    elif overdue_days >= 30:
        reasons.append(
            f"{overdue_days} روز تأخیر"
        )
    elif overdue_days > 0:
        reasons.append(
            f"{overdue_days} روز تأخیر"
        )
    else:
        reasons.append(
            "فاکتور هنوز معوق نشده است"
        )

    if debt_amount >= 500_000_000:
        reasons.append(
            "مبلغ بدهی بسیار بالا است"
        )
    elif debt_amount >= 200_000_000:
        reasons.append(
            "مبلغ بدهی بالا است"
        )
    elif debt_amount >= 100_000_000:
        reasons.append(
            "مبلغ بدهی قابل توجه است"
        )
    elif debt_amount > 0:
        reasons.append(
            "مانده بدهی وجود دارد"
        )

    return reasons


def calculate_risk(
    overdue_days,
    debt_amount,
):
    score = calculate_risk_score(
        overdue_days,
        debt_amount,
    )

    level = get_risk_level(score)

    reasons = get_risk_reasons(
        overdue_days,
        debt_amount,
    )

    return {
        "score": score,
        "level": level,
        "reasons": reasons,
    }