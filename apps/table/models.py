"""
Models of table app
"""
import time
import random
import hashlib
from typing import Type
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.management import call_command

from table.utils.column_handlers import IntegerColumnHandler


def column_settings_default():
    """Generator of default values for field settigns"""
    return {}


class Table(models.Model):
    """Table entity"""

    name = models.CharField(_("Name"), max_length=64, unique=True)
    slug = models.CharField(_("Slug"), max_length=64, unique=True)
    options = models.JSONField(_("Options"), default=dict)

    def __init__(self, *args, **kwargs) -> None:
        """Initialize table"""
        super().__init__(*args, **kwargs)

        if not self.slug:
            code = time.time_ns() + random.randint(1, 10)
            self.slug = "talbe_" + hashlib.md5(str(code).encode())\
                        .hexdigest()

    def add_column(self, column_name: str, dtype: int) -> None:
        """Add new column to table"""
        self.columns.add(Column(name=column_name, dtype=dtype))

    def get_model(self) -> None:
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
        model = type(self.slug, (models.Model,), attrs)
        print(model._meta.db_table)
        # Create an Admin class if admin options were provided
        return model


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
        DType.INTEGER: IntegerColumnHandler
    }

    name = models.CharField(_("Name"), max_length=64, unique=True)
    slug = models.CharField(_("Slug"), max_length=64, unique=True)
    dtype = models.IntegerField(_("Data type"), choices=DType)
    settings = models.JSONField(_("Settings"), default=dict)

    table = models.ForeignKey(Table, on_delete=models.CASCADE,
                              related_name="columns")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not self.slug:
            code = time.time_ns() + random.randint(1, 10)
            self.slug = "column_" + hashlib.md5(str(code).encode())\
                        .hexdigest()

        self.handler = self.HANDLERS[self.dtype](self.name, self.slug, self.settings)

    def get_django_model_field(self) -> Type[models.Field]:
        """
        Return django field column depending on column type
        """
        return self.handler.get_model_field()
