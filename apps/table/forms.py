"""Forms of table app"""
from django import forms
from django.forms import inlineformset_factory 
from django.utils.translation import gettext_lazy as _

from table.models import Table, Column


class TableEditForm(forms.Form):
    """TableEditForm"""

    name = forms.CharField(label=_("Name"), max_length=64)
    description = forms.CharField(label=_("Description"), widget=forms.Textarea())


class ColumnEditForm(forms.ModelForm):
    """ColumnEditForm"""

    class Meta:
        model = Column
        exclude = ('slug', 'settings',)

    name = forms.CharField(label=_("Column name"))
    dtype = forms.ChoiceField(label=_("DType"), choices=Column.DType)

ColumnFormSet = inlineformset_factory(Table, Column, form=ColumnEditForm, extra=1)
