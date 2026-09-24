import os
import uuid

import pandas as pd

from django.conf import settings
from django.shortcuts import render

from risk.risk_engine import calculate_risk


def upload_file(request):
    uploaded_file = None
    columns = []
    preview = None
    sheet_names = []
    selected_sheet = None
    df = None
    summary = None

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        selected_sheet = request.POST.get("sheet")

        # مرحله اول: آپلود فایل
        if uploaded_file:
            file_name = uploaded_file.name.lower()

            if file_name.endswith((".xlsx", ".xls")):
                temp_dir = os.path.join(
                    settings.BASE_DIR,
                    "temp_uploads",
                )

                os.makedirs(temp_dir, exist_ok=True)

                temp_name = f"{uuid.uuid4()}_{uploaded_file.name}"
                temp_path = os.path.join(
                    temp_dir,
                    temp_name,
                )

                with open(temp_path, "wb+") as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                request.session["uploaded_excel_path"] = temp_path

                excel_file = pd.ExcelFile(temp_path)
                sheet_names = excel_file.sheet_names

                if selected_sheet:
                    df = pd.read_excel(
                        temp_path,
                        sheet_name=selected_sheet,
                    )
                else:
                    df = pd.read_excel(
                        temp_path,
                        sheet_name=0,
                    )

            elif file_name.endswith(".csv"):
                encodings = [
                    "utf-8-sig",
                    "cp1256",
                    "windows-1252",
                    "latin1",
                ]

                for encoding in encodings:
                    try:
                        uploaded_file.seek(0)

                        df = pd.read_csv(
                            uploaded_file,
                            encoding=encoding,
                        )

                        break

                    except UnicodeDecodeError:
                        continue

            else:
                return render(
                    request,
                    "imports/upload.html",
                    {
                        "error": (
                            "Only CSV and Excel files are allowed."
                        ),
                    },
                )

        # مرحله دوم: انتخاب Sheet بدون آپلود دوباره
        else:
            temp_path = request.session.get(
                "uploaded_excel_path"
            )

            if temp_path and os.path.exists(temp_path):
                excel_file = pd.ExcelFile(temp_path)
                sheet_names = excel_file.sheet_names

                if selected_sheet:
                    df = pd.read_excel(
                        temp_path,
                        sheet_name=selected_sheet,
                    )
                else:
                    df = pd.read_excel(
                        temp_path,
                        sheet_name=0,
                    )

            else:
                return render(
                    request,
                    "imports/upload.html",
                    {
                        "error": (
                            "Please upload the Excel file first."
                        ),
                    },
                )

        # بررسی ستون‌های موردنیاز
        if df is not None:

            df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace("\u200c", "", regex=False)
            .str.replace("ي", "ی", regex=False)
            .str.replace("ك", "ک", regex=False)
        )


            required_columns = [
                "شماره فاکتور",
                "کد مشتری",
                "تاریخ فاکتور",
                "مبلغ فاکتور",
                "مهلت پرداخت",
                "مبلغ پرداختشده",
                "مانده",
            ]

            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:
                return render(
                    request,
                    "imports/upload.html",
                    {
                        "error": (
                            "ستون‌های زیر در Sheet پیدا نشدند: "
                            + "، ".join(missing_columns)
                        ),
                        "uploaded_file": uploaded_file,
                        "sheet_names": sheet_names,
                        "selected_sheet": selected_sheet,
                    },
                )

            # تمیز کردن داده‌ها

            date_columns = [
                "تاریخ فاکتور",
                "مهلت پرداخت",
            ]

            for column in date_columns:
                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce",
                )


            amount_columns = [
                "مبلغ فاکتور",
                "مبلغ پرداختشده",
                "مانده",
            ]

            for column in amount_columns:
                df[column] = (
                    df[column]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("٬", "", regex=False)
                    .str.strip()
                )

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce",
                )


            # اعتبارسنجی داده‌ها

            validation_errors = []

            if df["شماره فاکتور"].isna().any():
                validation_errors.append("بعضی ردیف‌ها شماره فاکتور ندارند.")

            if df["کد مشتری"].isna().any():
                validation_errors.append("بعضی ردیف‌ها کد مشتری ندارند.")

            if df["تاریخ فاکتور"].isna().any():
                validation_errors.append("بعضی تاریخ‌های فاکتور نامعتبر هستند.")

            if df["مهلت پرداخت"].isna().any():
                validation_errors.append("بعضی مهلت‌های پرداخت نامعتبر هستند.")

            for column in amount_columns:
                if df[column].isna().any():
                    validation_errors.append(
                        f"بعضی مقادیر ستون «{column}» نامعتبر هستند."
                    )

            # محاسبه روزهای تأخیر

            today = pd.Timestamp.today().normalize()

            df["روزهای تأخیر"] = (
                today - df["مهلت پرداخت"]
            ).dt.days

            df["روزهای تأخیر"] = (
                df["روزهای تأخیر"]
                .clip(lower=0)
            )


            # محاسبه مانده واقعی

            df["مانده واقعی"] = (
                df["مبلغ فاکتور"] - df["مبلغ پرداختشده"]
            )


            # وضعیت سررسید

            df["وضعیت"] = "سررسید نشده"

            df.loc[
                (df["مانده واقعی"] > 0)
                & (df["روزهای تأخیر"] > 0),
                "وضعیت",
            ] = "معوق"

            df.loc[
                df["مانده واقعی"] <= 0,
                "وضعیت",
            ] = "تسویه شده"


            # محاسبه ریسک برای هر ردیف

            risk_results = df.apply(
                lambda row: calculate_risk(
                    row["روزهای تأخیر"],
                    row["مانده واقعی"],
                ),
                axis=1,
            )

            df["Risk Score"] = risk_results.apply(
                lambda result: result["score"]
            )

            df["Risk Level"] = risk_results.apply(
                lambda result: result["level"]
            )

            df["Risk Reasons"] = risk_results.apply(
                lambda result: "، ".join(result["reasons"])
            )


            # خلاصه مالی

            total_receivables = df["مانده واقعی"].sum()

            total_overdue = df.loc[
                df["وضعیت"] == "معوق",
                "مانده واقعی",
            ].sum()

            overdue_invoice_count = (
                df["وضعیت"] == "معوق"
            ).sum()

            overdue_customer_count = df.loc[
                df["وضعیت"] == "معوق",
                "کد مشتری",
            ].nunique()

            overdue_percentage = 0

            if total_receivables > 0:
                overdue_percentage = (
                    total_overdue / total_receivables
                ) * 100


            summary = {
                "total_receivables": total_receivables,
                "total_overdue": total_overdue,
                "overdue_invoice_count": overdue_invoice_count,
                "overdue_customer_count": overdue_customer_count,
                "overdue_percentage": overdue_percentage,
            }

            # ستون‌ها و Preview
            columns = df.columns.tolist()

            preview = df.head(5).to_html(
                index=False,
                classes="preview-table",
            )

    return render(
        request,
        "imports/upload.html",
        {
            "uploaded_file": uploaded_file,
            "columns": columns,
            "preview": preview,
            "sheet_names": sheet_names,
            "selected_sheet": selected_sheet,
            "summary": summary,
        },
    )