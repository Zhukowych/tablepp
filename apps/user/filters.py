import django_filters
from .models import User, Role
from ajax_select.fields import AutoCompleteSelectWidget


class UserListFilter(django_filters.FilterSet):
    """Filterset UserList"""

    class META:
        """META class"""

        model = User
        fields = ["user", "role"]

    user = django_filters.CharFilter(
        field_name="username",
        lookup_expr="icontains",
        label="User: ",
    )

    role = django_filters.ModelChoiceFilter(
        field_name="role",
        lookup_expr="exact",
        label="Role: ",
        queryset=Role.objects.all(),
    )
