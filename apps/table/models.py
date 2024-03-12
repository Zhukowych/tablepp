"""
Models of table app
"""
from __future__ import annotations

import time
import random
import hashlib
from typing import Type

import django_filters
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from table.utils.column_handlers import IntegerColumnHandler, TextColumnHandler
from table.utils.dynamic_model import DynamicModelMixin, DynamicModelFormMixin, DynamicModelFilterSetMixin
from core.forms import BaseModelForm


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
            self.slug = "talbe_" + hashlib.md5(str(code).encode())\
                        .hexdigest()

    def __str__(self) -> str:
        """Return a string representation of Table"""
        return repr(self)

    def __repr__(self) -> str:
        """Return a string representation of Table"""
        return f"Table(name={self.name})"

    def get_absolute_url(self) -> str:
        """Return url to Table edit page"""
        return reverse('table-edit', kwargs={'table_id': self.id})

    def get_displayable_columns(self) -> QuerySet[Column]:
        """Return list of columns that can be displayed in talbe"""
        return self.columns.filter(is_displayble=True)

    def get_filterable_columns(self) -> QuerySet[Column]:
        """Return list of columns that can be present in filters"""
        return self.columns.filter(is_filterable=True)

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
        """Create tab"""

        class Meta:
            """Meta for dynammic_model"""

        # we must set the app_label and table name
        setattr(Meta, 'app_label', 'table')
        setattr(Meta, 'db_table', self.slug)

        # Update Meta with any options that were provided
        if self.options is not None:
            for key, value in self.options.items():
                setattr(Meta, key, value)

        # Set up a dictionary to simulate declarations within a class
        attrs = {'__module__': 'apps.table', 'Meta': Meta}

        # Add in any fields that were provided
        for column in self.columns.all():
            attrs[column.slug] = column.get_django_model_field()

        # Create the class, which automatically triggers ModelBase processing
        model = type(self.slug, (models.Model, DynamicModelMixin), attrs)
        setattr(model, 'table', self)
        # Create an Admin class if admin options were provided
        return model

    def get_model_form(self) -> ModelForm:
        """
        Create model form for table.
        Form for adding and editing
        """
        class Meta:
            """Meta for talbe's model form"""

        setattr(Meta, "model", self.get_model())
        setattr(Meta, "fields", "__all__")

        model_form = type(f"{self.slug}ModelForm", (BaseModelForm, DynamicModelFormMixin),
                           {'Meta':Meta})
        return model_form

    def get_filterset(self) -> django_filters.FilterSet:
        """
        Create FilterSet class for table
        """

        class Meta:
            """FilterSet Meta"""

        filterable_columns = self.get_filterable_columns()
        fields_filters = {
            column.slug: column.get_filters_names()
            for column in filterable_columns
        }

        setattr(Meta, 'model', self.get_model())
        setattr(Meta, 'fields', fields_filters)
        print(fields_filters)
        filterset = type(f"table_{self.slug}FilterSet",
                         (DynamicModelFilterSetMixin, django_filters.FilterSet),
                         {"Meta": Meta})

        return filterset


class Column(models.Model):
    """Field entity"""

    class DType(models.IntegerChoices):
        """enum for types of columns"""
        TEXT = 0, _("Text")
        INTEGER = 1, _("Integer")
        POSITIVE_INTEGER = 2, _("Positive integer")
        FLOAT = 3, _("Float")
        BIG_TEXT = 4, _("Big text")

    HANDLERS = {
        DType.TEXT: TextColumnHandler,
        DType.INTEGER: IntegerColumnHandler
    }

    name = models.CharField(_("Name"), max_length=64, unique=True)
    slug = models.CharField(_("Slug"), max_length=64, unique=True)
    dtype = models.IntegerField(_("Data type"), choices=DType, default=DType.INTEGER)
    settings = models.JSONField(_("Settings"), default=dict)

    is_filterable = models.BooleanField(_("Filterable?"), default=True)
    is_displayable = models.BooleanField(_("Displayable?"), default=True)

    table = models.ForeignKey(Table, on_delete=models.CASCADE,
                              related_name="columns")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.slug:
            code = time.time_ns() + random.randint(1, 10)
            self.slug = "column_" + hashlib.md5(str(code).encode())\
                        .hexdigest()

        self.handler = self.HANDLERS[self.dtype](self.name, self.slug, self.settings)

    def __repr__(self) -> str:
        """Return a string representation of Column"""
        return f"Column(name={self.name})"

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
