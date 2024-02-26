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
        return render(request, "dashboard.html", {})


class TableListView(View):
    """List all dynamic tables"""


class TableEditView(View):
    """Edit dynamic table"""


class TableView(View):
    """Edit dynamic table"""


class TableObjectEditView(View):
    """Table object edit view"""


class TableObjectDeleteView(View):
    """Table object edit view"""


class TablePermissions(View):
    """List table permissioins"""


class ImportTableDataView(View):
    """Import table data view"""


class ExportTableDataView(View):
    """Import table data view"""
