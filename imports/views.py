from django.shortcuts import render


def upload_file(request):
    uploaded_file = None

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

    return render(
        request,
        "imports/upload.html",
        {"uploaded_file": uploaded_file},
    )
