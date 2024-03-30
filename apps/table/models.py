"""
Models of table app
"""

from __future__ import annotations

import time
import random
import hashlib
import traceback
from typing import Type

import django_filters
from ajax_select import registry
from ajax_select.fields import AutoCompleteSelectWidget
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from table.utils.column_handlers import (
    IntegerColumnHandler,
    TextColumnHandler,
    FloatColumnHandler,
    BigTextColumnHandler,
)
from table.utils.dynamic_model import (
    DynamicModelMixin,
    DynamicModelFormMixin,
    DynamicModelFilterSetMixin,
)
from core.forms import BaseModelForm
from user.models import TablePermission, User

from apps.table.utils.column_handlers import RelationColumnHandler
from apps.table.utils.dynamic_model import DynamicModelLookup


def column_settings_default():
    """Generator of default values for field settigns"""
    return {}


class Table(models.Model):
    """Table entity"""

    name = models.CharField(_("Name"), max_length=64, unique=True)
    description = models.CharField(_("Table descriptioni"), max_length=256, null=True)
    slug = models.CharField(_("Slug"), max_length=64, unique=True)
    options = models.JSONField(_("Options"), default=dict)

    def __init__(self, *args, **kwargs) -> None:
        """Initialize table"""
        super().__init__(*args, **kwargs)

        if not self.slug:
            code = time.time_ns() + random.randint(1, 10)
            self.slug = "table_" + hashlib.md5(str(code).encode()).hexdigest()

    def __str__(self) -> str:
        """Return a string representation of Table"""
        return repr(self)

    def __repr__(self) -> str:
        """Return a string representation of Table"""
        return f"Table(name={self.name})"

    @property
    def searchable_column(self):
        return self.columns.filter(dtype=Column.DType.TEXT).first() or self.columns.first()

    def get_absolute_url(self) -> str:
        """Return url to Table edit page"""
        return reverse("table-edit", kwargs={"table_id": self.id})

    def get_displayable_columns(self, user) -> QuerySet[Column]:
        """Return list of columns that can be displayed in talbe"""
        displayable_columns = [
            column
            for column in self.columns.filter(is_displayable=True)
            if user.has_permission(TablePermission.Operation.READ, column)
        ]
        return displayable_columns

    def get_filterable_columns(self) -> QuerySet[Column]:
        """Return list of columns that can be present in filters"""
        return self.columns.all()

    def add_column(self, column_name: str, dtype: int) -> None:
        """Add new column to table"""
        self.columns.add(Column(name=column_name, dtype=dtype))

    def remove_column(self, column: str | Column) -> None:
        """
        Remove column from table. Column also removes from db
        """
        if isinstance(column, Column):
            column.delete()
        if isinstance(column, str):
            column = self.columns.get(name=column)
            column.delete()
        raise ValueError("You must pass column object either column name to delete it.")

    def get_model(self) -> models.Model:
        """Create model"""

        class Meta:
            """Meta for dynammic_model"""

        # we must set the app_label and table name
        setattr(Meta, "app_label", "table")
        setattr(Meta, "db_table", self.slug)

        # Update Meta with any options that were provided
        if self.options is not None:
            for key, value in self.options.items():
                setattr(Meta, key, value)

        # Set up a dictionary to simulate declarations within a class
        attrs = {"__module__": "apps.table", "Meta": Meta}

        # Add in any fields that were provided
        for column in self.columns.all():
            try:
                attrs[column.slug] = column.get_django_model_field()
            except Exception as ex:
                traceback.print_exc()

        # Create the class, which automatically triggers ModelBase processing
        model = type(self.slug, (DynamicModelMixin, models.Model), attrs)
        setattr(model, "table", self)
        # Create an Admin class if admin options were provided
        return model

    def get_model_form(self, user: User) -> BaseModelForm:
        """
        Create model form for table.
        Form for adding and editing
        """

        class Meta:
            """Meta for talbe's model form"""

        displayable_columns = self.get_displayable_columns(user)
        displayable_column_names = [field.slug for field in displayable_columns]
        setattr(Meta, "model", self.get_model())
        setattr(Meta, "fields", displayable_column_names)

        model_form = type(
            f"{self.slug}ModelForm",
            (DynamicModelFormMixin, BaseModelForm),
            {"Meta": Meta},
        )

        readonly_columns = [
            column
            for column in displayable_columns
            if not user.has_permission(TablePermission.Operation.WRITE, column)
        ]
        setattr(model_form, "columns", self.columns.all())
        setattr(model_form, "readlonly_columns", readonly_columns)

        return model_form

    def register_ajax_lookup(self):
        """Add ajax lookup to table"""

        attrs = {
            'model': self.get_model(),
            'searchable_column': self.searchable_column
        }

        lookup_channel = type(f"{self.slug}LookupChannel", (DynamicModelLookup, ), attrs)
        registry.register({self.slug: lookup_channel})

    def get_filterset(self) -> django_filters.FilterSet:
        """
        Create FilterSet class for table
        """

        class Meta:
            """FilterSet Meta"""

        filterable_columns = self.get_filterable_columns()
        fields_filters = {
            column.slug: column.get_filters_names() for column in filterable_columns
        }
        attrs = {"Meta": Meta}

        setattr(Meta, "model", self.get_model())
        setattr(Meta, "fields", fields_filters)

        for column in filterable_columns:
            if column.dtype == Column.DType.RELATION and fields_filters[column.slug]:
                content_type = ContentType.objects.get(id=column.settings.get('content_type_id'))
                table = Table.objects.get(slug=content_type.model)

                def filter_function(cls, queryset, _, value):
                    return queryset.filter(**{f"{column.slug}_id": value.id})

                filter_method_name = f"{column.slug}_filter"
                attrs[column.slug] = django_filters.ModelChoiceFilter(
                    queryset=table.get_model().objects.all(),
                    widget=AutoCompleteSelectWidget(table.slug),
                    label=column.name,
                    method=filter_method_name)

                attrs[filter_method_name] = filter_function

        filterset = type(
            f"table_{self.slug}FilterSet",
            (DynamicModelFilterSetMixin, django_filters.FilterSet),
            attrs
        )

        return filterset

    def get_dependent_tables(self) -> list["Table"]:
        """
        Return list of tables that are dependent on this table
        through relation
        """
        content_type = ContentType.objects.get(model=self.slug)
        relation_columns = Column.objects.filter(dtype=Column.DType.RELATION)
        dependent_tables = []
        for relation_columns in relation_columns:
            related_content_type_id = relation_columns.settings.get('content_type_id')
            if int(related_content_type_id) == content_type.id:
                dependent_tables.append(relation_columns.table)
        return dependent_tables

    def get_related_objects_of_table(self, table: "Table", object) -> QuerySet:
        model = self.get_model()
        fields = model._meta.get_fields()
        for field in fields:
            if isinstance(field, models.ManyToOneRel) and field.related_model.__name__ == table.slug:
                return field.related_model.objects.filter(**{field.related_name: object.id})


class Column(models.Model):
    """Field entity"""

    class Meta:
        """Model settings"""

        unique_together = ("name", "table")

    class DType(models.IntegerChoices):
        """enum for types of columns"""

        TEXT = 0, _("Text")
        INTEGER = 1, _("Integer")
        FLOAT = 3, _("Float")
        BIG_TEXT = 4, _("Big text")
        RELATION = 5, _("Relationship")

    HANDLERS = {
        DType.TEXT: TextColumnHandler,
        DType.INTEGER: IntegerColumnHandler,
        DType.RELATION: RelationColumnHandler,
        DType.FLOAT: FloatColumnHandler,
        DType.BIG_TEXT: BigTextColumnHandler,
    }

    name = models.CharField(_("Name"), max_length=64)
    slug = models.CharField(_("Slug"), max_length=64, unique=True)
    dtype = models.IntegerField(_("Data type"), choices=DType, default=DType.INTEGER)
    settings = models.JSONField(_("Settings"), default=dict)

    is_filterable = models.BooleanField(_("Filterable?"), default=True)
    is_displayable = models.BooleanField(_("Displayable?"), default=True)

    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="columns")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.slug:
            code = time.time_ns() + random.randint(1, 10)
            self.slug = "column_" + hashlib.md5(str(code).encode()).hexdigest()

        self.handler = self.HANDLERS[self.dtype](self.name, self.slug, self.settings)

    def __repr__(self) -> str:
        """Return a string representation of Column"""
        return f"Column(table={self.table.name}, name={self.name})"

    def __str__(self) -> str:
        return repr(self)

    def get_django_model_field(self) -> Type[models.Field]:
        """
        Return django field column depending on column type
        """
        return self.handler.get_model_field()

    def get_filters_names(self) -> list[str]:
        """
        Return list of finters that can be applied to column
        i.e lte, gte, etc
        """
        return self.handler.get_filters()

    def get_table_formating_class(self) -> str:
        """
        Return css class to format this field
        """
        return self.handler.get_css_formating_class()
