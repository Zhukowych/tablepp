"""Forms of table app"""
import django_filters
from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from apps.core.forms import BaseModelForm, BaseFilterSet
from table.models import Table, Column


class TableForm(BaseModelForm):
    """TableForm"""

    class Meta:
        """Meta for TableForm"""
        model = Table
        fields = ["name", 'description']

    description = forms.CharField(widget=forms.Textarea())


class TableFilter(BaseFilterSet):
    """FIlter for tables"""

    class Meta:
        """Meta for TableFilter"""
        model = Table
        fields = ["name"]


class ColumnEditForm(BaseModelForm):
    """ColumnEditForm"""

    class Meta:
        model = Column
        exclude = ('slug', 'table')

    name = forms.CharField(label=_("Column name"))
    dtype = forms.ChoiceField(label=_("DType"), choices=Column.DType)
    settings = forms.CharField(label=_("Settings"), widget=forms.HiddenInput(), initial="{}")

    def is_valid(self) -> bool:
        if not self.cleaned_data:
            return True
        return super().is_valid()


ColumnFormSet = inlineformset_factory(Table, Column, form=ColumnEditForm, extra=1)
