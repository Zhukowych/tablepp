"""Forms of table app"""
from django import forms
from django.forms import inlineformset_factory 
from django.utils.translation import gettext_lazy as _

from table.models import Table, Column


class ColumnEditForm(forms.ModelForm):
    """ColumnEditForm"""

    class Meta:
        model = Column
        exclude = ('slug', )

    name = forms.CharField(label=_("Column name"))
    dtype = forms.ChoiceField(label=_("DType"), choices=Column.DType)
    settings = forms.CharField(label=_("Settings"), widget=forms.HiddenInput(), initial="{}")

    def is_valid(self) -> bool:
        if not self.cleaned_data:
            return True
        return super().is_valid()


ColumnFormSet = inlineformset_factory(Table, Column, form=ColumnEditForm, extra=1)
