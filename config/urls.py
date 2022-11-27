"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from luggages.views import admin_luggagebill_detail, admin_customer_detail, admin_trip_luggages, homepage

urlpatterns = [
    path('admin/luggages/luggagebill/<int:luggagebill_id>/', 
        admin_luggagebill_detail, 
        name='admin_luggagebill_detail'),
    path('admin/luggages/customer/<int:customer_id>/', 
        admin_customer_detail, 
        name='admin_customer_detail'),
    path('admin/luggages/trip/<int:trip_id>/', 
        admin_trip_luggages, 
        name='admin_trip_luggages'),

    path('admin/', admin.site.urls),

    path('', homepage, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'Backend Admin'
admin.site.index_title = 'Luggage Billing System'
admin.site.site_title = 'Admin Dashboard'
