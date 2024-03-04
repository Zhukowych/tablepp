from django import forms


class UpdateUserGroupForm(forms.Form):
    name = forms.CharField()
    group_select = forms.ModelChoiceField(queryset=None)
