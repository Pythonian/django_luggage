from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from luggages.views import (
    admin_customer_detail,
    admin_luggagebill_detail,
    admin_trip_luggages,
    homepage,
)

urlpatterns = [
    path(
        "admin/luggages/luggagebill/<int:luggagebill_id>/",
        admin_luggagebill_detail,
        name="admin_luggagebill_detail",
    ),
    path(
        "admin/luggages/customer/<int:customer_id>/",
        admin_customer_detail,
        name="admin_customer_detail",
    ),
    path(
        "admin/luggages/trip/<int:trip_id>/",
        admin_trip_luggages,
        name="admin_trip_luggages",
    ),
    path("admin/", admin.site.urls),
    path("", homepage, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Luggager Admin"
admin.site.index_title = "Luggager Billing System"
admin.site.site_title = "Luggager Admin Dashboard"
