"""Forms"""
import django_filters
from django import forms
from django.forms import ModelForm


class BaseModelForm(ModelForm):
    """Base Model Form"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field, forms.ChoiceField):
                visible.field.widget.attrs['class'] = 'select-input input-field'
            elif isinstance(visible.field, forms.BooleanField):
                visible.field.widget.attrs['class'] = 'checkbox-input'
            else:
                visible.field.widget.attrs['class'] = 'input-field'
        for visible_field in self.visible_fields():
            existing_classes = visible_field.field.widget.attrs.get('class', '')
            if visible_field.errors:
                visible_field.field.widget.attrs['class'] = existing_classes + " invalid_field"


class BaseForm(forms.Form):
    """Base form"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field, forms.ChoiceField):
                visible.field.widget.attrs['class'] = 'select-input input-field'
            elif isinstance(visible.field, forms.BooleanField):
                visible.field.widget.attrs['class'] = 'checkbox-input'
            else:
                visible.field.widget.attrs['class'] = 'input-field'


class BaseFilterSet(django_filters.FilterSet):
    """BaseFilterSet"""


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for visible in self.form.visible_fields():
            if isinstance(visible.field, forms.ChoiceField):
                visible.field.widget.attrs['class'] = 'select-input input-field'
            elif isinstance(visible.field, forms.BooleanField):
                visible.field.widget.attrs['class'] = 'checkbox-input'
            else:
                visible.field.widget.attrs['class'] = 'input-field'