"""Views of table app"""
from typing import Any

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.db import transaction

from table.models import Table, Column
from table.forms import ColumnEditForm, ColumnFormSet
from apps.table.utils.utils import migrate


class DasboardView(View):
    """View of dashboard page"""

    def get(self, request, *args, **kwargs):
        """
        Process get requests. Return general data about system
        """
        return render(request, "dashboard.html", {})


class TableListView(ListView):
    """List all dynamic tables"""
    model = Table
    paginate_by = 10


class SaveTableMixin:
    """
    Mixin for saving Table object in 
    both create and update views
    """

    def form_valid(self, form):
        """Do action when create form is valid"""
        context = self.get_context_data()
        columns_form = context['columns_form']

        if any( error for error in columns_form.errors[:-1]):
            return self.form_invalid(form)
        with transaction.atomic():
            self.object = form.save(commit=True)
            columns_form.instance = self.object
            for column_form in columns_form.forms:
                if column_form.is_valid():
                    column = column_form.save(commit=False)
                    column.table = self.object
                    column.save()
        migrate()
        return super().form_valid(form)

    def form_invalid(self, form):
        """If form is not valid"""
        return super().form_invalid(form)


class TableCreateView(SaveTableMixin, CreateView):
    """Edit dynamic table"""
    model = Table
    fields = ['name', 'description']
    success_url = reverse_lazy('table-list')

    def get_context_data(self, **kwargs) -> dict:
        """Return context of the view"""
        context = super().get_context_data(**kwargs)
        context['columns_form'] = ColumnFormSet(self.request.POST or None)
        context['dtypes'] = Column.HANDLERS
        return context

class TableUpdateView(SaveTableMixin, UpdateView):
    """Update Table view"""

    model = Table
    fields = ['name', 'description']
    pk_url_kwarg = "table_id"
    template_name_suffix = "_form"

    def get_context_data(self, **kwargs) -> dict:
        """Return context of the view"""
        context = super().get_context_data(**kwargs)
        context['columns_form'] = ColumnFormSet(self.request.POST or None, instance=self.object)
        context['dtypes'] = Column.HANDLERS
        return context


class HasPermissionMixin:
    """Check if user has permissions to do action"""

    operation = None

    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)

class TableObjectListView(ListView):
    """List objects added to table"""
    template_name = "table/object_list.html"
    paginate_by = 10
    table = None
    formset = None

    def get(self, request, table_id: int=None):
        """List all objects in the table"""
        self.table = Table.objects.get(pk=table_id)
        self.model = self.table.get_model()
        queryset = self.table.get_model().objects.all()
        self.formset = self.table.get_filterset()(self.request.GET, queryset=queryset)
        self.queryset = self.formset.qs
        return super().get(request, table_id=table_id)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Modify rendering context"""
        context = super().get_context_data(**kwargs)
        context['table'] = self.table
        context['filter'] = self.formset
        return context


class DynamicModelViewMixin:
    """
    Mixin for setting up generic create and
    update views to usage with dynamic tables
    """

    table = None

    def get(self, request, table_id: int, *args, **kwargs):
        """Get method for object creationg"""
        self.setup_view(table_id)
        return super().get(request=request, table_id=table_id, *args, **kwargs)

    def post(self, request, table_id: int, *args, **kwargs):
        """Get method for object creationg"""
        self.setup_view(table_id)
        return super().post(request=request, table_id=table_id, *args, **kwargs)

    def setup_view(self, table_id):
        """
        Setup CreateView to useage with dynamic model
        """
        self.table = Table.objects.get(pk=table_id)
        self.fields = self.table.columns.values_list('slug', flat=True)
        self.model = self.table.get_model()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Change context for view"""
        context = super().get_context_data(**kwargs)
        context['table'] = self.table
        return context


class TableObjectCreateView(DynamicModelViewMixin, CreateView):
    """Create table objects"""

    template_name = "table/object_form.html"


class TableObjectEditView(DynamicModelViewMixin, UpdateView):
    """Table object edit view"""

    template_name = "table/object_form.html"
    pk_url_kwarg = "object_id"


class TableObjectDeleteView(View):
    """Table object edit view"""


class TablePermissions(View):
    """List table permissioins"""


class ImportTableDataView(View):
    """Import table data view"""


class ExportTableDataView(View):
    """Import table data view"""
