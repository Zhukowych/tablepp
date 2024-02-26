"""Views of table app"""
from django.shortcuts import render
from django.views import View

from table.models import Table, Column
from apps.table.utils.utils import migrate


class DasboardView(View):
    """View of dashboard page"""

    def get(self, request, *args, **kwargs):
        """
        Process get requests. Return general data about system
        """
        migrate()
        return render(request, "dashboard.html", {})
