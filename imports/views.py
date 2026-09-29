import os
import uuid

import pandas as pd

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companies.models import UserProfile
from customers.models import Customer
from invoices.models import Invoice

from risk.risk_engine import calculate_risk
from risk.services import calculate_company_risks


# نام‌های مختلفی که ممکن است شرکت‌ها برای هر فیلد استفاده کنند.
COLUMN_ALIASES = {
    "invoice_number": [
        "شماره فاکتور",
        "شماره سند",
        "شماره صورتحساب",
        "شماره صورتحساب فروش",
        "شماره فاکتور فروش",
        "invoice number",
        "invoice_number",
    ],
    "customer_code": [
        "کد مشتری",
        "شناسه مشتری",
        "شماره مشتری",
        "کد طرف حساب",
        "شناسه طرف حساب",
        "customer code",
        "customer_code",
    ],
    "invoice_date": [
        "تاریخ فاکتور",
        "تاریخ صدور",
        "تاریخ سند",
        "تاریخ صورتحساب",
        "تاریخ فاکتور فروش",
        "invoice date",
        "invoice_date",
    ],
    "invoice_amount": [
        "مبلغ فاکتور",
        "مبلغ کل",
        "مبلغ ناخالص",
        "مبلغ فروش",
        "مبلغ سند",
        "مبلغ صورتحساب",
        "invoice amount",
        "invoice_amount",
        "amount",
    ],
    "paid_amount": [
        "مبلغ پرداختشده",
        "مبلغ پرداخت شده",
        "مبلغ وصولی",
        "مبلغ وصول شده",
        "پرداختی",
        "وصولی",
        "جمع پرداخت",
        "paid amount",
        "paid_amount",
    ],
    "due_date": [
        "مهلت پرداخت",
        "تاریخ سررسید",
        "سررسید",
        "تاریخ سررسید فاکتور",
        "due date",
        "due_date",
    ],
}


FIELD_LABELS = {
    "invoice_number": "شماره فاکتور",
    "customer_code": "کد مشتری",
    "invoice_date": "تاریخ فاکتور",
    "invoice_amount": "مبلغ فاکتور",
    "paid_amount": "مبلغ پرداخت‌شده",
    "due_date": "مهلت پرداخت",
}


REQUIRED_FIELDS = [
    "invoice_number",
    "customer_code",
    "invoice_date",
    "invoice_amount",
    "paid_amount",
    "due_date",
]


def normalize_column_name(value):
    return (
        str(value)
        .strip()
        .replace("\u200c", "")
        .replace("ي", "ی")
        .replace("ك", "ک")
        .replace(" ", "")
        .replace("_", "")
        .lower()
    )


def find_auto_mapping(columns):
    mapping = {}

    normalized_columns = {
        normalize_column_name(column): column
        for column in columns
    }

    for field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            normalized_alias = normalize_column_name(alias)

            if normalized_alias in normalized_columns:
                mapping[field] = normalized_columns[normalized_alias]
                break

    return mapping


def get_mapping_fields(columns, auto_mapping):
    fields = []

    for field in REQUIRED_FIELDS:
        fields.append(
            {
                "key": field,
                "label": FIELD_LABELS[field],
                "selected": auto_mapping.get(field, ""),
                "columns": columns,
            }
        )

    return fields


def clean_dataframe_columns(df):
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\u200c", "", regex=False)
        .str.replace("ي", "ی", regex=False)
        .str.replace("ك", "ک", regex=False)
    )

    return df


def process_dataframe(df, company):
    df = df.copy()

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
        validation_errors = []

    if df["شماره فاکتور"].isna().any():
        validation_errors.append(
            "بعضی ردیف‌ها شماره فاکتور ندارند."
        )

    if df["کد مشتری"].isna().any():
        validation_errors.append(
            "بعضی ردیف‌ها کد مشتری ندارند."
        )

    if df["تاریخ فاکتور"].isna().any():
        validation_errors.append(
            "بعضی تاریخ‌های فاکتور نامعتبر هستند."
        )

    if df["مهلت پرداخت"].isna().any():
        validation_errors.append(
            "بعضی مهلت‌های پرداخت نامعتبر هستند."
        )

    for column in amount_columns:
        if df[column].isna().any():
            validation_errors.append(
                f"بعضی مقادیر ستون «{column}» نامعتبر هستند."
            )

    if validation_errors:
        return df, validation_errors

    today = pd.Timestamp.today().normalize()

    df["روزهای تأخیر"] = (
        today - df["مهلت پرداخت"]
    ).dt.days

    df["روزهای تأخیر"] = (
        df["روزهای تأخیر"]
        .clip(lower=0)
    )

    df["مانده واقعی"] = (
        df["مبلغ فاکتور"]
        - df["مبلغ پرداختشده"]
    )

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
        lambda result: "، ".join(
            result["reasons"]
        )
    )

    if company:
        for _, row in df.iterrows():
            customer_code = str(
                row["کد مشتری"]
            ).strip()

            customer, _ = Customer.objects.get_or_create(
                company=company,
                code=customer_code,
                defaults={
                    "name": customer_code,
                },
            )

            invoice_number = str(
                row["شماره فاکتور"]
            ).strip()

            Invoice.objects.update_or_create(
                company=company,
                invoice_number=invoice_number,
                defaults={
                    "customer": customer,
                    "amount": row["مبلغ فاکتور"],
                    "paid_amount": row["مبلغ پرداختشده"],
                    "invoice_date": row["تاریخ فاکتور"].date(),
                    "due_date": row["مهلت پرداخت"].date(),
                },
            )

        calculate_company_risks(company)

    return df, []


@login_required
def upload_file(request):

    profile = (
        UserProfile.objects
        .select_related("company")
        .filter(user=request.user)
        .first()
    )

    company = profile.company if profile else None

    uploaded_file_name = request.session.get(
        "uploaded_file_name"
    )

    selected_sheet = request.session.get(
        "selected_sheet"
    )

    temp_path = request.session.get(
        "uploaded_excel_path"
    )

    df = None
    sheet_names = []
    columns = []
    preview = None
    summary = None
    mapping_fields = None
    auto_mapping = {}
    mapping_error = None

    # -----------------------------------------
    # مرحله ۱: آپلود فایل
    # -----------------------------------------

    if request.method == "POST" and request.FILES.get("file"):

        uploaded_file = request.FILES.get("file")
        file_name = uploaded_file.name.lower()

        request.session["uploaded_file_name"] = (
            uploaded_file.name
        )

        if file_name.endswith((".xlsx", ".xls")):

            temp_dir = os.path.join(
                settings.BASE_DIR,
                "temp_uploads",
            )

            os.makedirs(
                temp_dir,
                exist_ok=True,
            )
            temp_name = (
                f"{uuid.uuid4()}_{uploaded_file.name}"
            )

            temp_path = os.path.join(
                temp_dir,
                temp_name,
            )

            with open(
                temp_path,
                "wb+",
            ) as destination:

                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            request.session[
                "uploaded_excel_path"
            ] = temp_path

            excel_file = pd.ExcelFile(
                temp_path
            )

            sheet_names = excel_file.sheet_names

            selected_sheet = (
                request.POST.get("sheet")
                or sheet_names[0]
            )

            request.session[
                "selected_sheet"
            ] = selected_sheet

            df = pd.read_excel(
                temp_path,
                sheet_name=selected_sheet,
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

            selected_sheet = None

        else:

            return render(
                request,
                "imports/upload.html",
                {
                    "error": (
                        "فقط فایل‌های CSV و Excel مجاز هستند."
                    ),
                },
            )

        if df is not None:

            df = clean_dataframe_columns(df)

            columns = df.columns.tolist()

            auto_mapping = find_auto_mapping(
                columns
            )

            mapping_fields = get_mapping_fields(
                columns,
                auto_mapping,
            )

    # -----------------------------------------
    # مرحله ۲: انتخاب Sheet
    # -----------------------------------------

    elif (
        request.method == "POST"
        and request.POST.get("action")
        == "select_sheet"
    ):

        selected_sheet = request.POST.get(
            "sheet"
        )

        temp_path = request.session.get(
            "uploaded_excel_path"
        )

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            excel_file = pd.ExcelFile(
                temp_path
            )

            sheet_names = (
                excel_file.sheet_names
            )

            df = pd.read_excel(
                temp_path,
                sheet_name=selected_sheet,
            )

            df = clean_dataframe_columns(df)

            columns = df.columns.tolist()

            auto_mapping = find_auto_mapping(
                columns
            )

            mapping_fields = get_mapping_fields(
                columns,
                auto_mapping,
            )

            request.session[
                "selected_sheet"
            ] = selected_sheet

    # -----------------------------------------
    # مرحله ۳: تأیید Mapping و Import
    # -----------------------------------------

    elif (
        request.method == "POST"
        and request.POST.get("action")
        == "apply_mapping"
    ):

        temp_path = request.session.get(
            "uploaded_excel_path"
        )

        selected_sheet = request.session.get(
            "selected_sheet"
        )

        if temp_path and os.path.exists(temp_path):

            if temp_path.lower().endswith(".csv"):

                df = pd.read_csv(
                    temp_path,
                    encoding="utf-8-sig",
                )

            else:
                df = pd.read_excel(
                    temp_path,
                    sheet_name=selected_sheet,
                )

            df = clean_dataframe_columns(df)

            columns = df.columns.tolist()

            selected_mapping = {}

            for field in REQUIRED_FIELDS:

                selected_column = request.POST.get(
                    f"mapping_{field}"
                )

                if selected_column:
                    selected_mapping[field] = (
                        selected_column
                    )

            missing_fields = [
                FIELD_LABELS[field]
                for field in REQUIRED_FIELDS
                if not selected_mapping.get(field)
            ]

            if missing_fields:

                mapping_error = (
                    "برای فیلدهای زیر ستون انتخاب نشده است: "
                    + "، ".join(missing_fields)
                )

                auto_mapping = find_auto_mapping(
                    columns
                )

                mapping_fields = get_mapping_fields(
                    columns,
                    auto_mapping,
                )

            else:

                mapped_columns = list(
                    selected_mapping.values()
                )

                if len(mapped_columns) != len(
                    set(mapped_columns)
                ):

                    mapping_error = (
                        "یک ستون نمی‌تواند برای چند فیلد مختلف استفاده شود."
                    )

                    mapping_fields = get_mapping_fields(
                        columns,
                        selected_mapping,
                    )

                else:

                    df = df.rename(
                        columns={
                            selected_mapping[
                                "invoice_number"
                            ]: "شماره فاکتور",

                            selected_mapping[
                                "customer_code"
                            ]: "کد مشتری",

                            selected_mapping[
                                "invoice_date"
                            ]: "تاریخ فاکتور",

                            selected_mapping[
                                "invoice_amount"
                            ]: "مبلغ فاکتور",

                            selected_mapping[
                                "paid_amount"
                            ]: "مبلغ پرداختشده",

                            selected_mapping[
                                "due_date"
                            ]: "مهلت پرداخت",
                        }
                    )

                    df, validation_errors = (
                        process_dataframe(
                            df,
                            company,
                        )
                    )

                    if validation_errors:

                        mapping_error = " ".join(
                            validation_errors
                        )

                        mapping_fields = (
                            get_mapping_fields(
                                columns,
                                selected_mapping,
                            )
                        )

                    else:

                        total_receivables = (
                            df["مانده واقعی"].sum()
                        )

                        total_overdue = (
                            df.loc[
                                df["وضعیت"] == "معوق",
                                "مانده واقعی",
                            ].sum()
                        )

                        overdue_invoice_count = (
                            df["وضعیت"] == "معوق"
                        ).sum()

                        overdue_customer_count = (
                            df.loc[
                                df["وضعیت"] == "معوق",
                                "کد مشتری",
                            ].nunique()
                        )
                        overdue_percentage = 0

                        if total_receivables > 0:

                            overdue_percentage = (
                                total_overdue
                                / total_receivables
                            ) * 100

                        summary = {
                            "total_receivables":
                                total_receivables,

                            "total_overdue":
                                total_overdue,

                            "overdue_invoice_count":
                                overdue_invoice_count,

                            "overdue_customer_count":
                                overdue_customer_count,

                            "overdue_percentage":
                                overdue_percentage,
                        }

                        columns = (
                            df.columns.tolist()
                        )

                        preview = df.head(
                            5
                        ).to_html(
                            index=False,
                            classes="preview-table",
                        )

                        # پاک‌سازی فایل موقت
                        try:
                            os.remove(temp_path)
                        except OSError:
                            pass

                        request.session.pop(
                            "uploaded_excel_path",
                            None,
                        )

                        request.session.pop(
                            "uploaded_file_name",
                            None,
                        )

                        request.session.pop(
                            "selected_sheet",
                            None,
                        )

    # -----------------------------------------
    # اطلاعات Sheet برای نمایش
    # -----------------------------------------

    if temp_path and os.path.exists(temp_path):

        if temp_path.lower().endswith(
            (".xlsx", ".xls")
        ):

            excel_file = pd.ExcelFile(
                temp_path
            )

            sheet_names = (
                excel_file.sheet_names
            )

    return render(
        request,
        "imports/upload.html",
        {
            "uploaded_file": uploaded_file_name,
            "columns": columns,
            "preview": preview,
            "sheet_names": sheet_names,
            "selected_sheet": selected_sheet,
            "summary": summary,
            "mapping_fields": mapping_fields,
            "mapping_error": mapping_error,
        },
    )