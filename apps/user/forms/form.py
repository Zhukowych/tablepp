from typing import Any, Mapping
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
import django_filters
from django import forms
from django.forms import modelformset_factory
from django.contrib.contenttypes.models import ContentType
from ajax_select.fields import AutoCompleteSelectWidget, AutoCompleteSelectField
from user.models import TablePermission, User


class UpdateUserGroupForm(forms.Form):
    name = forms.CharField()
    group_select = forms.ModelChoiceField(queryset=None)


PERMITTABLE_CONTENT_TYPES = ContentType.objects.filter(model__in=['table', 'column']).order_by('model')


class TablePermissionsFilter(django_filters.FilterSet):
    """Filterset for permissions"""

    class Meta:
        """Meta"""
        model = TablePermission
        fields = ['type', 'operation', 'content_type', 'user']

    user = django_filters.ModelChoiceFilter(
                field_name="user",
                label="User",

                queryset=User.objects.all(),
                widget=AutoCompleteSelectWidget("user"))

class TablePermissionForm(forms.ModelForm):
    """TablePermission form"""

    class Meta:
        """Meta for ModelForm"""
        model = TablePermission
        exclude = ('object_id', )

    content_type = forms.ModelChoiceField(queryset=PERMITTABLE_CONTENT_TYPES, required=True)
    table = AutoCompleteSelectField("table", required=False)
    column = AutoCompleteSelectField("column", required=False)

    def __init__(self, *args, instance=None, **kwargs):
        """Initialize form""" 
        super().__init__(*args, instance=instance, **kwargs)

        if not self.instance.object:
            return

        if self.instance.content_type.model == "table":
            self.fields['table'].initial = self.instance.object_id
        else:
            self.fields['column'].initial = self.instance.object_id

    def clean(self):
        """Check overall form correctness"""
        if not self.cleaned_data.get('table') and not self.cleaned_data.get('column'):
            raise forms.ValidationError("You must specify table or column to" + \
                                        " which to add this permission")

    def save(self, commit=True):
        """Save created instance"""
        permission = super().save(commit=False)
        if not self.cleaned_data:
            return

        if self.cleaned_data['content_type'].model == "table":
            object = self.cleaned_data['table']
        else:
            object = self.cleaned_data['column']

        permission.object = object

        if commit:
            permission.save()
        return permission


TablePermissionFormSet = modelformset_factory(model=TablePermission, form=TablePermissionForm)
