import os
import uuid

import pandas as pd

from django.conf import settings
from django.shortcuts import render


def upload_file(request):
    uploaded_file = None
    columns = []
    preview = None
    sheet_names = []
    selected_sheet = None

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        selected_sheet = request.POST.get("sheet")

        # مرحله اول: آپلود فایل
        if uploaded_file:
            file_name = uploaded_file.name.lower()

            if file_name.endswith((".xlsx", ".xls")):
                temp_dir = os.path.join(settings.BASE_DIR, "temp_uploads")
                os.makedirs(temp_dir, exist_ok=True)

                temp_name = f"{uuid.uuid4()}_{uploaded_file.name}"
                temp_path = os.path.join(temp_dir, temp_name)

                with open(temp_path, "wb+") as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                request.session["uploaded_excel_path"] = temp_path

                excel_file = pd.ExcelFile(temp_path)
                sheet_names = excel_file.sheet_names

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

                df = None

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
                        "error": "Only CSV and Excel files are allowed.",
                    },
                )

        # مرحله دوم: انتخاب Sheet
        else:
            temp_path = request.session.get("uploaded_excel_path")

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
                        "error": "Please upload the Excel file first.",
                    },
                )

        if df is not None:
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
        },
    )