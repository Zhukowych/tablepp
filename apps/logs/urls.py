"""Urls for logs app"""
from django.urls import path
from logs.views import LogsListView

from apps.logs.views import LogDetailView

urlpatterns = [
    path('', LogsListView.as_view(), name="logs-list"),
    path('<int:log_id>/', LogDetailView.as_view(), name="log-detail"),

]
