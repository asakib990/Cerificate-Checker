from certificatechecker.settings import STATIC_URL
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path("", views.homeView, name="home"),
    path("validate/", views.validate, name="validate"),
]

admin.site.site_header = 'ADMIN'
