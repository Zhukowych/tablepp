"""Views of table app"""
import json
from typing import Any
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse

from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db import transaction
from django.contrib import messages

from table.models import Table, Column
from user.models import TablePermission
from table.forms import  TableForm, ColumnFormSet, TableFilter
from logs.models import Logs
from logs.utils import log
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

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.filter = None

    def get(self, request: HttpRequest) -> HttpResponse:
        """get method processor"""
        self.filter = TableFilter(self.request.GET or None, queryset=Table.objects.all())
        self.queryset = self.filter.qs
        return super().get(request)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context

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
    form_class = TableForm
    success_url = reverse_lazy('table-list')

    def get_context_data(self, **kwargs) -> dict:
        """Return context of the view"""
        context = super().get_context_data(**kwargs)
        context['columns_form'] = ColumnFormSet(self.request.POST or None)
        context['dtypes'] = Column.HANDLERS
        context['table'] = self.object
        return context

class TableUpdateView(SaveTableMixin, UpdateView):
    """Update Table view"""

    model = Table
    form_class = TableForm
    pk_url_kwarg = "table_id"
    template_name_suffix = "_form"

    def get_context_data(self, **kwargs) -> dict:
        """Return context of the view"""
        context = super().get_context_data(**kwargs)
        context['columns_form'] = ColumnFormSet(self.request.POST or None, instance=self.object)
        context['dtypes'] = Column.HANDLERS
        context['table'] = self.object
        return context


class HasPermissionMixin:
    """Check if user has permissions to do action"""

    operation = None
    table_attr = ''
    redirect_url = 'table-list'

    def dispatch(self, request, *args, **kwargs):
        """Check if user has permission"""
        http_response = super().dispatch(request, *args, **kwargs)
        if request.user.has_permission(self.operation, self.table):
            return http_response
        else:
            messages.error(request, "You have no permission to access this page")
            return redirect(self.get_reject_url())

    def get_reject_url(self) -> None:
        """Return reserve to which redirect if has no permission"""
        return reverse('table-list')


class TableObjectListView(HasPermissionMixin, ListView):
    """List objects added to table"""
    template_name = "table/object_list.html"
    paginate_by = 2
    table = None
    formset = None
    operation = TablePermission.Operation.READ

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


class DynamicModelViewMixin(HasPermissionMixin):
    """
    Mixin for setting up generic create and
    update views to usage with dynamic tables
    """

    table = None
    form_class = None
    operation = TablePermission.Operation.WRITE

    def get_reject_url(self) -> None:
        return reverse('object-list', args=[self.table.id])

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
        self.form_class = self.table.get_model_form(self.request.user)
        self.model = self.table.get_model()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Change context for view"""
        context = super().get_context_data(**kwargs)
        context['table'] = self.table
        return context

    def dump_object(self) -> str:
        """Convert current state of object to str"""
        object_dict = {
            column.name: getattr(self.object, column.slug)
            for column in self.table.columns.all()
        }
        return json.dumps(object_dict)


class TableObjectCreateView(DynamicModelViewMixin, CreateView):
    """Create table objects"""

    template_name = "table/object_form.html"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        log(
            user=self.request.user,
            table=self.table,
            object_id=self.object.id,
            message="Created object"
        )
        return response

class TableObjectEditView(DynamicModelViewMixin, UpdateView):
    """Table object edit view"""

    template_name = "table/object_form.html"
    pk_url_kwarg = "object_id"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        before_update = self.dump_object()
        response = super().form_valid(form)
        after_update = self.dump_object()
        log(
            user=self.request.user,
            table=self.table,
            object_id=self.object.id,
            message="Changed Xobject",
            description=f"Changed object from {before_update} -> {after_update}"
        )
        return response

class TableObjectDeleteView(DynamicModelViewMixin, DeleteView):
    """Table object edit view"""

    operation = TablePermission.Operation.DELETE
    template_name = "table/object_delete.html"
    pk_url_kwarg = "object_id"

    def form_valid(self, *args, **kwargs):
        before_deletions = self.dump_object()
        log(
            user=self.request.user,
            table=self.table,
            object_id=self.object.id,
            message="Deleted object",
            description=f"Deleted object {before_deletions}"
        )       
        return super().form_valid(*args, **kwargs)

    def get_success_url(self) -> str:
        return reverse('object-list', args=[self.table.id])


class ImportTableDataView(View):
    """Import table data view"""


class ExportTableDataView(View):
    """Import table data view"""
