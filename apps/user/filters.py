import django_filters
from .models import User, Role, UserGroups
from core.forms import BaseFilterSet


class UserListFilter(BaseFilterSet):
    """Filterset UserList"""

    class META:
        """META class"""

        model = User
        fields = ["user", "role"]

    user = django_filters.CharFilter(
        field_name="username",
        lookup_expr="icontains",
        label="User",
    )

    role = django_filters.ModelChoiceFilter(
        field_name="role",
        lookup_expr="exact",
        label="Role",
        queryset=Role.objects.all(),
    )


class RoleListFilter(BaseFilterSet):
    """Filterset for Role"""

    class META:
        """META class"""

        model = Role
        fields = ["role"]

    role = django_filters.CharFilter(
        field_name="role",
        lookup_expr="icontains",
        label="Role",
    )


class GroupListFilter(BaseFilterSet):
    """Filterset for Role"""

    class META:
        """META class"""

        model = UserGroups
        fields = ["name"]

    groups = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="Groups",
    )
