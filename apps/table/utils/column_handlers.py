"""
A set of classes for converting Columns to 
djnago classes
"""

import json

from abc import ABC, abstractmethod
from enum import Enum

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Field, IntegerField, CharField, FloatField, TextField
from django import forms
from django.utils.translation import gettext_lazy as _

from annotated_types import Any


class ColumnHandler(ABC):
    """
    ColumnHandler is a class for converting table.models.Column
    to django fields
    """

    form = None

    def __init__(self, name: str, slug: str, settings: dict) -> None:
        """Initialize ColumnHandler"""
        self.name = name
        self.slug = slug
        self.settings = (
            json.loads(settings) if not isinstance(settings, dict) else settings
        )

    @abstractmethod
    def get_model_field(self) -> Field:
        """Return model field for column"""

    @abstractmethod
    def get_css_formating_class(self) -> Field:
        """Return css class to format table col"""

    @abstractmethod
    def validate_value(self, value) -> bool:
        """Validate value or raise ValidationError"""

    @abstractmethod
    def format_value(self, value) -> str:
        """Formats value"""

    @classmethod
    def get_settings_form(cls) -> forms.Form:
        """Return an instance of column setting form"""
        return cls.settings_form()

    def get_filters(self) -> list[str]:
        """
        Return list of finters that can be applied to column
        i.e lte, gte, etc
        """
        return self.settings.get("filters", [])

    def get_kwargs(self) -> tuple[list, dict]:
        """
        Return default kwargs of django model field
        """
        return {"null": True, "blank": True}


class ColumnSettingsForm(forms.Form):
    """Column settings forms"""

    template_name = ""

    filters = forms.MultipleChoiceField(
        label=_("Filters"), widget=forms.CheckboxSelectMultiple, choices=[]
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        choices = [
            (filter_type.value[0], filter_type.value[1]) for filter_type in self.Filters
        ]
        self.fields["filters"].choices = choices


class IntegerSettingsForm(ColumnSettingsForm):
    """Integer field settings form"""

    DEFAULT_MIN_VALUE = -100
    DEFAULT_MAX_VALUE = 100

    template_name = "settings_form/integer_column_form.html"

    class Filters(Enum):
        """filters for"""

        GTE = "gte", _("Greater or equal")
        LTE = "lte", _("Less or equal")

    class Meta:
        field_order = ["filters", "min_value", "max_value"]

    min_value = forms.IntegerField(label=_("Min value"), initial=DEFAULT_MIN_VALUE)
    max_value = forms.IntegerField(label=_("Max value"), initial=DEFAULT_MAX_VALUE)


class FloatSettingsForm(ColumnSettingsForm):
    """Integer field settings form"""

    DEFAULT_MIN_VALUE = -100.0
    DEFAULT_MAX_VALUE = 100.0

    template_name = "settings_form/float_column_form.html"

    class Filters(Enum):
        """filters for"""

        GTE = "gte", _("Greater or equal")
        LTE = "lte", _("Less or equal")

    class Meta:
        """Meta class"""

        field_order = ["filters", "min_value", "max_value"]

    min_value = forms.FloatField(label=_("Min value"), initial=DEFAULT_MIN_VALUE)
    max_value = forms.FloatField(label=_("Max value"), initial=DEFAULT_MAX_VALUE)


class TextSettingForm(ColumnSettingsForm):
    """Text column settings form"""

    DEFAULT_MAX_LENGTH = 128

    class Filters(Enum):
        """Filters for text column"""

        EXACT = "exact", _("Exact value")
        CONTAINS = "contains", _("Contains")

    template_name = "settings_form/text_column_form.html"

    max_length = forms.IntegerField(label=_("Max length"), initial=DEFAULT_MAX_LENGTH)

    class Meta:
        """Meta class"""

        field_order = ["filters", "max_length"]


class BigTextSettingForm(ColumnSettingsForm):
    """Text column settings form"""

    class Filters(Enum):
        """Filters for text column"""

        EXACT = "exact", _("Exact value")
        CONTAINS = "contains", _("Contains")

    template_name = "settings_form/text_column_form.html"

    class Meta:
        """Meta class"""

        field_order = ["filters"]


RELATABLE_MODELS = ContentType.objects.filter(
    model__startswith="table_"
) | ContentType.objects.filter(model="user")


class RelationColumnSettingForm(ColumnSettingsForm):
    class Filters(Enum):
        """Filters for relation column"""

        EXACT = "exact", _("Exact value")

    template_name = "settings_form/relation_column_form.html"

    content_type = forms.ModelChoiceField(queryset=RELATABLE_MODELS)


class IntegerColumnHandler(ColumnHandler):
    """Handler for IntegerColumn"""

    settings_form = IntegerSettingsForm

    def get_model_field(self) -> Field:
        kwargs = self.get_kwargs()
        return IntegerField(_(self.name), **kwargs)

    def get_css_formating_class(self) -> Field:
        return "integer"

    def validate_value(self, value) -> bool:
        min_value = (
            self.settings.get("min_value") or IntegerSettingsForm.DEFAULT_MIN_VALUE
        )
        max_value = (
            self.settings.get("max_value") or IntegerSettingsForm.DEFAULT_MAX_VALUE
        )
        if not min_value <= value <= max_value:
            raise forms.ValidationError(
                f"Value must be between {min_value} and {max_value}"
            )
        return True

    def format_value(self, value: int) -> int:
        """Formats value"""
        return value


class FloatColumnHandler(ColumnHandler):
    """Handler for FloatColumn"""

    settings_form = FloatSettingsForm

    def get_model_field(self) -> Field:
        kwargs = self.get_kwargs()
        return FloatField(_(self.name), **kwargs)

    def get_css_formating_class(self) -> Field:
        return "float"

    def validate_value(self, value) -> bool:
        min_value = (
            self.settings.get("min_value") or FloatSettingsForm.DEFAULT_MIN_VALUE
        )
        max_value = (
            self.settings.get("max_value") or FloatSettingsForm.DEFAULT_MAX_VALUE
        )
        if not min_value <= value <= max_value:
            raise forms.ValidationError(
                f"Value must be between {min_value} and {max_value}"
            )
        return True

    def format_value(self, value: float) -> float:
        """Formats value"""
        return value


class TextColumnHandler(ColumnHandler):
    """Handler for IntegerColumn"""

    settings_form = TextSettingForm

    def get_model_field(self) -> Field:
        kwargs = self.get_kwargs()
        return CharField(_(self.name), max_length=64, **kwargs)

    def get_css_formating_class(self) -> Field:
        return "text"

    def validate_value(self, value: str) -> bool:
        """Validate text field"""
        max_length = (
            self.settings.get("max_length") or TextSettingForm.DEFAULT_MAX_LENGTH
        )
        if len(value) > max_length:
            raise forms.ValidationError(
                f"Length must be less than or equal to {max_length}"
            )
        return True

    def format_value(self, value: str) -> str:
        """Formats value"""
        return value


class BigTextColumnHandler(ColumnHandler):
    """Handler for IntegerColumn"""

    settings_form = BigTextSettingForm

    def get_model_field(self) -> Field:
        kwargs = self.get_kwargs()
        return TextField(_(self.name), **kwargs)

    def get_css_formating_class(self) -> Field:
        return "Big text"

    def validate_value(self, value: str) -> bool:
        """Validate text field"""
        return True

    def format_value(self, value: str) -> str:
        """Formats value"""
        return value[:7] + "..."


class RelationColumnHandler(ColumnHandler):
    """Column handler for relation"""

    settings_form = RelationColumnSettingForm

    def get_css_formating_class(self) -> Field:
        return "text"

    def validate_value(self, value) -> bool:
        pass

    def get_model_field(self) -> Field:
        content_type_id = self.settings.get("content_type_id")
        content_type = ContentType.objects.get(id=content_type_id)
        if not content_type_id:
            raise ValueError("Model name must be specified in RelationColumn setting")

        return models.ForeignKey(f"{content_type.model}",
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 verbose_name=_(self.name))
