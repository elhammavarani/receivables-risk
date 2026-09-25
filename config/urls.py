from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from imports.views import upload_file
from dashboard.views import dashboard_home


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("imports/", include("imports.urls")),
    path("dashboard/", include("dashboard.urls")),

    path(
        "customers/",
        include("customers.urls"),
    ),
    
    path("", upload_file, name="home"),
]


