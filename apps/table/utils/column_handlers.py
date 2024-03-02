"""
A set of classes for converting Columns to 
djnago classes
"""
from abc import ABC, abstractmethod
from django.db.models import Field, IntegerField, CharField
from django import forms
from django.utils.translation import gettext_lazy as _


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
        self.settings = settings

    @abstractmethod
    def get_model_field(self) -> Field:
        """Return model field for column"""

    @classmethod
    def get_settings_form(cls) -> forms.Form:
        """Return an instance of column setting form"""
        return cls.settings_form()

    def get_kwargs(self) -> tuple[list, dict]:
        """
        Return default kwargs of django model field
        """
        return {'null': True, 'blank': True}


class ColumnSettingsForm(forms.Form):
    """Column settings forms"""

    template_name = ""


class IntegerSettigForm(ColumnSettingsForm):
    """Integer field settings form"""

    template_name = "settings_form/integer_column_form.html"

    min_value = forms.IntegerField(label=_("Min value"))
    max_value = forms.IntegerField(label=_("Max value"))


class TextSettingForm(ColumnSettingsForm):
    """Text column settings form"""

    template_name = "settings_form/text_column_form.html"

    max_length = forms.IntegerField(label=_("Max length"))


class IntegerColumnHandler(ColumnHandler):
    """Handler for IntegerColumn"""

    settings_form = IntegerSettigForm

    def get_model_field(self) -> Field:
        kwargs = self.get_kwargs()
        return IntegerField(_(self.name), **kwargs)

class TextColumnHandler(ColumnHandler):
    """Handler for IntegerColumn"""

    settings_form = TextSettingForm

    def get_model_field(self) -> Field:
        kwargs = self.get_kwargs()
        return CharField(_(self.name), max_length=64, **kwargs)
