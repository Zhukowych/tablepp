from django import forms
from user.models import User, UserGroups


class UpdateUserGroupForm(forms.Form):
    name = forms.CharField()
    group_select = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_groups = user.group_set.all()
        print(user_groups)
        self.fields["group_select"].queryset = Groups.objects.all()
