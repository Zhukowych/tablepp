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
    dtype = forms.ChoiceField(label=_("DType"), choices=Column.DType, required=False)
    settings = forms.JSONField(label=_("Settings"), widget=forms.HiddenInput(), initial=dict, required=False)

    def clean_dtype(self):
        """Return value of dtype if column is saved"""
        if self.instance.pk:
            return self.instance.dtype
        dtype = self.cleaned_data['dtype']
        if not dtype:
            raise forms.ValidationError("This field is required")
        return dtype

    def is_valid(self) -> bool:
        if not self.cleaned_data:
            return True
        return super().is_valid()


ColumnFormSet = inlineformset_factory(Table, Column, form=ColumnEditForm, extra=1)
