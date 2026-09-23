from django.contrib import admin
from django.urls import include, path
from imports.views import upload_file


urlpatterns = [
    path("admin/", admin.site.urls),
    path("imports/", include("imports.urls")),
    path("", upload_file, name="home"),
]


