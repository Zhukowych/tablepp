"""Forms"""

from typing import Any, Mapping
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
import django_filters
from django import forms
from django.forms import modelformset_factory, HiddenInput
from django.contrib.contenttypes.models import ContentType
from ajax_select.fields import AutoCompleteSelectWidget, AutoCompleteSelectField
from apps.core.forms import BaseModelForm
from user.models import TablePermission, User, UserGroups, Role
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class UpdateUserGroupForm(BaseModelForm):
    """Form for updating user's info"""

    class Meta:
        """Meta for ModelForm"""

        model = UserGroups
        fields = []

    group = AutoCompleteSelectField("group_name", required=True)


class UserForm(BaseModelForm):
    """UserForm"""

    password_confirm = forms.CharField(
        widget=forms.PasswordInput(), label="Confirm password", required=False
    )

    class Meta:
        """Meta class"""

        model = User
        fields = [
            "username",
            "password",
            "password_confirm",
            "email",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_superuser",
        ]

    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    def __init__(self, *args, **kwargs):
        is_superuser = kwargs.pop("is_superuser")
        super().__init__(*args, **kwargs)

        if not is_superuser:
            for field in self.fields:
                self.fields[field].widget.attrs["readonly"] = True
            self.fields["password"].widget.attrs["readonly"] = False
            self.fields["password_confirm"].widget.attrs["readonly"] = False

    def clean(self) -> dict[str, Any]:

        cleaned_data = super().clean()

        if cleaned_data["password"] != cleaned_data["password_confirm"]:
            self.add_error(
                "password_confirm", ValidationError("Passwords do not match.")
            )

        return cleaned_data

    # def is_valid(self) -> bool:

    # print(self.cleaned_data)

    # if self.cleaned_data["password"] != self.cleaned_data["password_confirm"]:
    # raise ValidationError("Passwords do not match.", code="invalid")

    # return super().is_valid()


class GroupForm(BaseModelForm):
    """Group model form"""

    class Meta:
        """Meta for GroupForm"""

        model = UserGroups
        fields = ["name"]


class RoleForm(BaseModelForm):
    """Role form"""

    class Meta:
        """Meta for RoleForm"""

        model = Role
        fields = ["role"]


PERMITTABLE_CONTENT_TYPES = ContentType.objects.filter(
    model__in=["table", "column"]
).order_by("model")


class TablePermissionsFilter(django_filters.FilterSet):
    """Filterset for permissions"""

    class Meta:
        """Meta"""

        model = TablePermission
        fields = ["type", "operation", "content_type", "user"]

    user = django_filters.ModelChoiceFilter(
        field_name="user",
        label="User",
        queryset=User.objects.all(),
        widget=AutoCompleteSelectWidget("user"),
    )


class TablePermissionForm(BaseModelForm):
    """TablePermission form"""

    class Meta:
        """Meta for ModelForm"""

        model = TablePermission
        exclude = ("object_id",)

    content_type = forms.ModelChoiceField(
        queryset=PERMITTABLE_CONTENT_TYPES, required=True
    )
    table = AutoCompleteSelectField("table", required=False)
    column = AutoCompleteSelectField("column", required=False)

    def __init__(self, *args, instance=None, **kwargs):
        """Initialize form"""
        super().__init__(*args, instance=instance, **kwargs)

        if not self.instance.object:
            return

        if self.instance.content_type.model == "table":
            self.fields["table"].initial = self.instance.object_id
        else:
            self.fields["column"].initial = self.instance.object_id

    def clean(self):
        """Check overall form correctness"""
        if not self.cleaned_data.get("table") and not self.cleaned_data.get("column"):
            raise forms.ValidationError(
                "You must specify table or column to" + " which to add this permission"
            )

    def save(self, commit=True):
        """Save created instance"""
        permission = super().save(commit=False)
        if not self.cleaned_data:
            return

        if self.cleaned_data["content_type"].model == "table":
            object = self.cleaned_data["table"]
        else:
            object = self.cleaned_data["column"]

        permission.object = object

        if commit:
            permission.save()
        return permission


TablePermissionFormSet = modelformset_factory(
    model=TablePermission, form=TablePermissionForm
)
