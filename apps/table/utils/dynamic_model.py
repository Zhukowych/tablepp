"""Dynamic model"""
from itertools import chain
from typing import Any

from ajax_select import LookupChannel
from ajax_select.fields import AutoCompleteSelectWidget
from django.contrib.contenttypes.models import ContentType
from django.db.models import ManyToOneRel, Model
from django.urls import reverse
from django import forms


class DynamicModelMixin:
    """Mixin class for dynamic models"""

    table = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        try:
            value = self.get_value_of(self.table.searchable_column)
            return value
        except AttributeError: # If referenced table was deleted
            return None

    def __repr__(self) -> str:
        return f"{self.table.name}(id={self.id})"

    def get_absolute_url(self) -> str:
        """Return url to Table edit page"""
        return reverse(
            "object-edit", kwargs={"table_id": self.table.id, "object_id": self.pk}
        )

    def get_value_of(self, column) -> Any:
        """Get value of column at this object"""
        return column.handler.format_value(getattr(self, column.slug))

    def get_all_relations(self):
        fields = self._meta.get_fields()
        return [field.related_model.objects.filter(**{field.related_name: self.id})
                for field in fields if isinstance(field, ManyToOneRel)]


class DynamicModelFormMixin:
    """Mixin class for ModelForm that uses dynamic model"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._create_autocomplete_fields()
        self._check_readonly_columns()

    def _check_readonly_columns(self) -> None:
        """Block fields for readonly columns """
        for readonly_column in self.readlonly_columns:
            self.fields[readonly_column.slug].widget.attrs["readonly"] = True

    def _create_autocomplete_fields(self):
        """Add autocomplete fields for ForeignKey columns"""
        for column in self.columns:
            if column.dtype != 5:
                continue

            content_type = ContentType.objects.get(id=column.settings.get("content_type_id"))
            self.fields[column.slug].widget = AutoCompleteSelectWidget(content_type.model,
                                                                       attrs={'class': 'input-field'})

    def clean(self):
        """Validate form data"""
        errors = {}
        for column in self.columns:
            field_value = self.cleaned_data.get(column.slug, '')
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
                visible.field.widget.attrs['class'] = 'input-field'


class DynamicModelLookup(LookupChannel):
    """Lookup for dynamic model"""

    model = None
    searchable_column = None

    def get_query(self, q, request):
        filtering_args = {f"{self.searchable_column.slug}__icontains": q}
        return self.model.objects.filter(**filtering_args).order_by(self.searchable_column.slug)[:50]

    def format_item_display(self, table_objects):
        """format on display"""
        return "<span>%s</span>" % str(table_objects)
