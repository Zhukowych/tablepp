"""Dynamic model"""

from typing import Any
from django.urls import reverse
from django import forms


class DynamicModelMixin:
    """Mixin class for dynamic models"""

    table = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Return url to Table edit page"""
        return reverse(
            "object-edit", kwargs={"table_id": self.table.id, "object_id": self.pk}
        )

    def get_value_of(self, column) -> Any:
        """Get value of column at this object"""
        print(getattr(self, column.slug), "what's going on")
        return column.handler.format_value(getattr(self, column.slug))


class DynamicModelFormMixin:
    """Mixin class for ModelForm that uses dynamic model"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for readonly_column in self.readlonly_columns:
            self.fields[readonly_column.slug].widget.attrs["readonly"] = True

    def clean(self):
        """Validate form data"""
        errors = {}
        for column in self.columns:
            field_value = self.cleaned_data[column.slug]
            print(field_value)
            try:

                column.handler.validate_value(field_value)
            except forms.ValidationError as error:
                errors[column.slug] = [error.message]

        if errors:
            raise forms.ValidationError(errors)


class DynamicModelFilterSetMixin:
    """Mixin class for FilterSet that works with dynamic model"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for visible in self.form.visible_fields():
            if isinstance(visible.field, forms.ChoiceField):
                visible.field.widget.attrs["class"] = "select-input input-field"
            elif isinstance(visible.field, forms.BooleanField):
                visible.field.widget.attrs["class"] = "checkbox-input"
            else:
                visible.field.widget.attrs["class"] = "input-field"
