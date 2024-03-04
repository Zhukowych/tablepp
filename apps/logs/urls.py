"""Urls for logs app"""
from django.urls import path
from logs.views import LogsListView


urlpatterns = [
    path('', LogsListView.as_view(), name="logs-list"),
]
