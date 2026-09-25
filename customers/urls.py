from django.urls import path

from .views import customer_detail


urlpatterns = [
    path(
        "<int:customer_id>/",
        customer_detail,
        name="customer_detail",
    ),
]