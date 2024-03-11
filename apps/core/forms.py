"""Forms"""
from django import forms
from django.forms import ModelForm

class BaseModelForm(ModelForm):
    """Base Model Form"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field, forms.ChoiceField):
                visible.field.widget.attrs['class'] = 'select-input input-field'
            else: 
                visible.field.widget.attrs['class'] = 'input-field'