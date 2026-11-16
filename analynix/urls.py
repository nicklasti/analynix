"""Analynix URL configuration."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("myapp.urls")),
]

handler404 = "myapp.views.error_404_view"
