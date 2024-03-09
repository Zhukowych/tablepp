import django_filters
from django import forms
from user.models import TablePermission

class UpdateUserGroupForm(forms.Form):
    name = forms.CharField()
    group_select = forms.ModelChoiceField(queryset=None)


class TablePermissionsFilter(django_filters.FilterSet):
    """Filter for permissions"""

    class Meta:
        """Meta"""
        model = TablePermission
        fields = ['type', 'operation', 'content_type']
