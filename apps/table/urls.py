"""Urls for table app"""
from django.urls import path
from .views import DasboardView


urlpatterns = [
    path('', DasboardView.as_view())
]
