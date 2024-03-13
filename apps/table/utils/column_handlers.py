"""
A set of classes for converting Columns to 
djnago classes
"""
import json

from abc import ABC, abstractmethod
from enum import Enum
from django.db.models import Field, IntegerField, CharField
from django import forms
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _

from easy_select2.widgets import Select2Multiple, Select2

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
        self.settings = json.loads(settings) if not isinstance(settings, dict) else settings

    @abstractmethod
    def get_model_field(self) -> Field:
        """Return model field for column"""

    @abstractmethod
    def get_css_formating_class(self) -> Field:
        """Return css class to format table col"""

    @classmethod
    def get_settings_form(cls) -> forms.Form:
        """Return an instance of column setting form"""
        return cls.settings_form()

    def get_filters(self) -> list[str]:
        """
        Return list of finters that can be applied to column
        i.e lte, gte, etc
        """
        return self.settings.get('filters', [])

    def get_kwargs(self) -> tuple[list, dict]:
        """
        Return default kwargs of django model field
        """
        return {'null': True, 'blank': True}


class ColumnSettingsForm(forms.Form):
    """Column settings forms"""

    template_name = ""

    filters = forms.MultipleChoiceField(label=_("Filters"),
                                        widget=forms.CheckboxSelectMultiple,
                                        choices=[])

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        choices = [ (filter_type.value[0], filter_type.value[1]) for filter_type in self.Filters]
        self.fields['filters'].choices = choices

class IntegerSettigForm(ColumnSettingsForm):
    """Integer field settings form"""

    template_name = "settings_form/integer_column_form.html"

    class Filters(Enum):
        """filters for """
        GTE = 'gte', _("Greater or equal")
        LTE = 'lte', _("Less or equal")

    class Meta:
        field_order = ['filters', 'min_value', 'max_value']

    min_value = forms.IntegerField(label=_("Min value"))
    max_value = forms.IntegerField(label=_("Max value"))


class TextSettingForm(ColumnSettingsForm):
    """Text column settings form"""

    class Filters(Enum):
        """Filters for text column"""
        EXACT = 'exact', _("Exact value")
        CONTAINS = 'contains', _("Contains")

    template_name = "settings_form/text_column_form.html"

    max_length = forms.IntegerField(label=_("Max length"))

    class Meta:
        field_order = ['filters', 'max_length']

class IntegerColumnHandler(ColumnHandler):
    """Handler for IntegerColumn"""

    settings_form = IntegerSettigForm

    def get_model_field(self) -> Field:
        kwargs = self.get_kwargs()
        return IntegerField(_(self.name), **kwargs)

    def get_css_formating_class(self) -> Field:
        return "integer"

class TextColumnHandler(ColumnHandler):
    """Handler for IntegerColumn"""

    settings_form = TextSettingForm

    def get_model_field(self) -> Field:
        kwargs = self.get_kwargs()
        return CharField(_(self.name), max_length=64, **kwargs)

    def get_css_formating_class(self) -> Field:
        return "text"
