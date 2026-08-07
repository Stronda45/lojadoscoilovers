"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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

from core.search_views import (
    search,
    vehicle_cars,
    vehicle_categories,
    vehicle_makes,
    vehicle_models,
)
from core.views import health, login, logout, orders, register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health', health),
    path('auth/register', register),
    path('auth/login', login),
    path('auth/logout', logout),
    path('orders', orders),
    path('vehicles/makes', vehicle_makes),
    path('vehicles/makes/<str:make_id>/models', vehicle_models),
    path('vehicles/cars', vehicle_cars),
    path('vehicles/<str:car_id>/categories', vehicle_categories),
    path('search', search),
]
