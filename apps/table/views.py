"""Views of table app"""
import os
import time
import openpyxl
from typing import Any
from datetime import datetime
from django.conf import settings

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse

from django.apps.registry import apps
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db import transaction
from django.contrib import messages
from markupsafe import Markup

from table.models import Table, Column
from user.models import TablePermission
from table.forms import TableForm, ColumnFormSet, TableFilter
from logs.utils import log
from apps.core.utils import IsUserAdminMixin

from apps.core.utils import BaseJSONEncoder
from apps.logs.utils import get_difference_dict
from apps.table.utils.utils import migrate


class DasboardView(View):
    """View of dashboard page"""

    def get(self, request, *args, **kwargs):
        """
        Process get requests. Return general data about system
        """
        return redirect("table-list")


class TableListView(ListView):
    """List all dynamic tables"""

    model = Table
    paginate_by = 10

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.filter = None

    def get(self, request: HttpRequest) -> HttpResponse:
        """get method processor"""
        self.filter = TableFilter(
            self.request.GET or None, queryset=Table.objects.all()
        )
        self.queryset = self.filter.qs
        return super().get(request)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter
        return context


class SaveTableMixin:
    """
    Mixin for saving Table object in
    both create and update views
    """

    def form_valid(self, form):
        """Do action when create form is valid"""
        context = self.get_context_data()
        columns_form = context["columns_form"]
        if any(error for error in columns_form.errors[:-1]):
            return self.form_invalid(form)
        with transaction.atomic():
            self.object = form.save(commit=True)
            columns_form.instance = self.object
            columns = []
            for column_form in columns_form.forms:
                if column_form.is_valid():
                    column = column_form.save(commit=False)
                    column.table = self.object
                    column.save()
                    columns.append(column)
            for column in self.object.columns.all():
                if column not in columns:
                    column.delete()

        migrate()
        self.object.register_ajax_lookup()
        return super().form_valid(form)

    def form_invalid(self, form):
        """If form is not valid"""
        return super().form_invalid(form)


class TableCreateView(SaveTableMixin, CreateView):
    """Edit dynamic table"""

    model = Table
    form_class = TableForm
    success_url = reverse_lazy("table-list")

    def get_context_data(self, **kwargs) -> dict:
        """Return context of the view"""
        context = super().get_context_data(**kwargs)
        context["columns_form"] = ColumnFormSet(self.request.POST or None)
        context["dtypes"] = Column.HANDLERS
        context["table"] = self.object
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
        context["columns_form"] = ColumnFormSet(
            self.request.POST or None, instance=self.object
        )
        context["dtypes"] = Column.HANDLERS
        context["table"] = self.object
        return context


class HasPermissionMixin:
    """Check if user has permissions to do action"""

    operation = None
    table_attr = ""
    redirect_url = "table-list"

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
        return reverse("table-list")


class TableObjectListView(HasPermissionMixin, ListView):
    """List objects added to table"""

    template_name = "table/object_list.html"
    paginate_by = 2
    table = None
    formset = None
    operation = TablePermission.Operation.READ

    table_id_kwarg = "table_id"

    def get(self, request,  *args, **kwargs):
        """List all objects in the table"""
        self.configure_view()
        return super().get(request, *args, **kwargs)

    def configure_view(self):
        self.table = Table.objects.get(pk=self.kwargs.get(self.table_id_kwarg))
        self.model = self.table.get_model()
        self.formset = self.table.get_filterset()(self.request.GET, queryset=self.get_queryset())
        self.queryset = self.formset.qs

    def get_queryset(self):
        return self.table.get_model().objects.all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Modify rendering context"""
        context = super().get_context_data(**kwargs)
        context["table"] = self.table
        context["filter"] = self.formset
        context['related_tables'] = self.table.get_dependent_tables()
        return context


class RelatedTableObjectsListView(TableObjectListView):

    template_name = "table/related_object_list.html"
    paginate_by = 10
    table = None
    parent_table = None
    table_object = None
    formset = None
    operation = TablePermission.Operation.READ

    table_id_kwarg = "related_table_id"
    parent_table_kwarg = "table_id"
    object_pk_kwarg = "object_id"

    def configure_view(self):
        self.parent_table = Table.objects.get(pk=self.kwargs.get(self.parent_table_kwarg))
        self.table_object = self.parent_table.get_model().objects.get(pk=self.kwargs.get(self.object_pk_kwarg))
        super().configure_view()

    def get_queryset(self) -> QuerySet:
        """Fetch related to table objects"""
        return self.parent_table.get_related_objects_of_table(self.table, self.table_object)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['parent_table'] = self.parent_table
        context['related_tables'] = self.parent_table.get_dependent_tables()
        context['object'] = self.table_object
        return context


class TableDeleteView(IsUserAdminMixin, DeleteView):
    pk_url_kwarg = "table_id"
    model = Table
    template_name = "table/table_delete.html"
    success_url = reverse_lazy("table-list")

    content_type = None

    def get_context_data(self, **kwargs) -> HttpResponse:
        """
        Check if deletion is safe and return context data.
        Add warning message if deletion is unsafe
        """
        context = super().get_context_data(**kwargs)

        if self._is_deletion_safe():
            context['safe'] = True
        else:
            messages.warning(self.request, self._get_deletion_prohibition_message(), extra_tags='safe')
            context['safe'] = False

        return context

    def form_valid(self, form):
        del apps.all_models['table'][self.object.slug]
        self.content_type = ContentType.objects.get(model=self.object.slug)
        self._delete_related_models()
        result = super().form_valid(form)
        migrate()
        return result

    def _is_deletion_safe(self) -> bool:
        """
        Check if there is no dependencies of this table
        Return the list of names of tables that depend on this table
        """
        return not bool(self.object.get_dependent_tables())

    def _delete_related_models(self) -> None:
        """Delete instances of ContentType, Permission and TablePermission"""
        django_permissions = Permission.objects.filter(content_type=self.content_type)
        table_permissions = TablePermission.objects.filter(object_id=self.object.id,
                                                           content_type=TablePermission.TABLE_CONTENT_TYPE)
        column_permissions = TablePermission.objects.filter(object_id__in=self.object.columns.values_list('id'),
                                                            content_type=TablePermission.COLUMN_CONTENT_TYPE)

        django_permissions.delete()
        table_permissions.delete()
        column_permissions.delete()
        self.content_type.delete()

    def _get_deletion_prohibition_message(self) -> Markup:
        """
        Return message about table deletion prohibition because other
        tables depend on this table
        """

        tables_hrefs = []
        for table in self.object.get_dependent_tables():
            tables_hrefs.append(mark_safe(f"<a href='{table.get_absolute_url()}' target='_blank'>{table.name}</a>"))

        return mark_safe(f"You cannot delete this table because other tables: {','.join(tables_hrefs)} are dependent on it")


class DynamicModelViewMixin(HasPermissionMixin):
    """
    Mixin for setting up generic create and
    update views to usage with dynamic tables
    """

    table = None
    operation = TablePermission.Operation.WRITE

    def get_reject_url(self) -> None:
        return reverse("object-list", args=[self.table.id])

    def get(self, request, table_id: int, *args, **kwargs):
        """Get method for object creationg"""
        for table in Table.objects.all():
            table.register_ajax_lookup()
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
        context["table"] = self.table
        return context

    def dump_object(self) -> dict:
        """Convert current state of object to str"""
        object_dict = {
            column.name: getattr(self.object, column.slug)
            for column in self.table.columns.all()
        }
        return object_dict


class TableObjectCreateView(DynamicModelViewMixin, CreateView):
    """Create table objects"""

    template_name = "table/object_form.html"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        log(
            user=self.request.user,
            table=self.table,
            object_id=self.object.id,
            message="Created object",
        )
        return response


class TableObjectEditView(DynamicModelViewMixin, UpdateView):
    """Table object edit view"""

    template_name = "table/object_form.html"
    pk_url_kwarg = "object_id"

    before_update = {}

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.before_update = self.dump_object()
        return self.object

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        after_update = self.dump_object()
        before_update, after_update = get_difference_dict(self.before_update, after_update)
        log(
            user=self.request.user,
            table=self.table,
            object_id=self.object.id,
            message="Changed object",
            description=f"Changed object from {before_update} -> {after_update}",
        )
        return response


class TableObjectDeleteView(DynamicModelViewMixin, DeleteView):
    """Table object edit view"""

    operation = TablePermission.Operation.DELETE
    template_name = "table/object_delete.html"
    pk_url_kwarg = "object_id"

    relations = None

    def setup_view(self, table_id: int) -> None:
        """Setup view"""
        self.table = Table.objects.get(pk=table_id)
        self.model = self.table.get_model()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        self.relations = self.object.get_all_relations()
        if self._is_deletion_safe():
            context['safe'] = True
        else:
            context['safe'] = False
            messages.error(self.request, self._get_deletion_prohibition_error())
        return context

    def form_valid(self, *args, **kwargs):
        before_deletions = self.dump_object()
        log(
            user=self.request.user,
            table=self.table,
            object_id=self.object.id,
            message="Deleted object",
            description=f"Deleted object {before_deletions}",
        )
        return super().form_valid(*args, **kwargs)

    def get_success_url(self) -> str:
        return reverse("object-list", args=[self.table.id])

    def _is_deletion_safe(self) -> bool:
        """
        Return True if deletion of object would not cause an error
        If there is not related objects to this
        """
        return not any(relation.all().exists() for relation in self.relations)

    def _get_deletion_prohibition_error(self) -> str:
        """
        Return message of deletion prohibition due to existence of related objects
        And include into message hrefs to that objects
        """
        related_objects = []

        for relation in self.relations:
            related_objects += list(relation.all())

        objects_to_include = related_objects[:10]
        hrefs = []

        for related_object in objects_to_include:
            hrefs.append(
                mark_safe(f"<a href='{related_object.get_absolute_url()}'>{repr(related_object)}</a>")
            )

        return f"You cannot delete this object, because {','.join(hrefs)} are related to it"


class ExportTableDataView(TableObjectListView):
    """Import table data view"""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.configure_view()

        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        worksheet.append(("Id", ) + tuple(column.name for column in self.table.columns.all()))

        for object in self.queryset:
            worksheet.append((object.id,) + tuple(str(object.get_repr_of(column))
                                                  for column in self.table.columns.all())
                             )
        path = os.path.join(settings.MEDIA_ROOT, f"{time.time_ns()}.xlsx")
        name = f"{self.table.name}_export_on_{datetime.now().strftime('%Y-%m-%d %H:%M')}.xlsx"

        workbook.save(path)

        response = HttpResponse(open(path, 'rb'), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(name)

        return response
