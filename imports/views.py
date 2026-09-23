import pandas as pd

from django.shortcuts import render


def upload_file(request):
    uploaded_file = None
    columns = []
    preview = None

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if uploaded_file:
            file_name = uploaded_file.name.lower()

            if file_name.endswith(".csv"):
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

            elif file_name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(uploaded_file)

            else:
                df = None

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
        },
    )