"""User app views"""

from typing import Any
from django.forms import BaseModelForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.hashers import make_password
from django.db import transaction

# from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from core.utils import IsUserAdminMixin
from django.db.models.query import QuerySet
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.hashers import make_password
from .models import User, Role, UserGroups, TablePermission
from .forms.form import (
    UpdateUserGroupForm,
    TablePermissionsFilter,
    TablePermissionForm,
    TablePermissionFormSet,
    UserForm,
    GroupForm,
    RoleForm,
)
from .filters import UserListFilter, RoleListFilter, GroupListFilter


class UserLoginView(LoginView):
    """View for login"""

    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        """to what url return a user on success"""

        user_pk = self.request.user.pk

        return reverse("update_user", kwargs={"pk": user_pk})


class UsersListView(ListView):
    """View for list of users"""

    model = User
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        self.filterset = UserListFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class RoleListView(ListView):
    """View for list of roles"""

    model = Role
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        self.filterset = RoleListFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class AddUserView(IsUserAdminMixin, CreateView):
    """View for creating user's users"""

    model = User
    form_class = UserForm
    template_name_suffix = "_update_form"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """hashes new user's password on validation of form"""
        user = form.save(commit=False)
        user.password = make_password(form.cleaned_data["password"])
        user.save()

        return super().form_valid(form)

    def get_success_url(self) -> str:
        """to what url to return on success"""
        return reverse("update_user", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["is_superuser"] = self.request.user.is_superuser
        return kwargs


class UpdateUserView(IsUserAdminMixin, UpdateView):
    """View for updating info about user"""

    model = User
    form_class = UserForm
    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):

        if request.user.pk == kwargs["pk"]:
            return UpdateView.dispatch(self, request, *args, **kwargs)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        """to what url to return on success"""
        return reverse("update_user", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """hashes password on save"""
        user = form.save(commit=False)
        user.password = make_password(form.cleaned_data["password"])
        user.save()

        return super().form_valid(form)

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["is_superuser"] = self.request.user.is_superuser
        return kwargs


class UserDeleteView(IsUserAdminMixin, DeleteView):
    """View for deleting user"""

    model = User
    success_url = reverse_lazy("user_list")


class AddRoleView(IsUserAdminMixin, CreateView):
    """View for adding roles"""

    model = Role
    form_class = RoleForm
    template_name_suffix = "_update_form"

    def get_success_url(self) -> str:
        """to what url to return on success"""
        return reverse("update_role", kwargs={"pk": self.object.pk})


class UpdateRoleView(IsUserAdminMixin, UpdateView):
    """View for updating roles name"""

    model = Role
    form_class = RoleForm
    template_name_suffix = "_update_form"
    redirect_url = "role_list"

    def get_success_url(self) -> str:
        """to what url to return on success"""
        return reverse("update_role", kwargs={"pk": self.object.pk})


class RoleDeleterView(IsUserAdminMixin, DeleteView):
    """View for deleting role"""

    model = Role
    success_url = reverse_lazy("role_list")


class GroupListView(ListView):
    """View for listing groups"""

    model = UserGroups
    template_name = "user/group_list.html"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        """get query set"""
        queryset = super().get_queryset()
        self.filterset = GroupListFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """get context data"""
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class AddGroupView(IsUserAdminMixin, CreateView):
    """View for adding groups"""

    model = UserGroups
    form_class = GroupForm
    template_name_suffix = "_update_form"

    def get_success_url(self) -> str:
        """to what url to return on success"""
        return reverse("edit_group", kwargs={"pk": self.object.pk})


class UpdateGroupView(IsUserAdminMixin, UpdateView):
    """View for updating group info"""

    model = UserGroups
    form_class = GroupForm
    template_name_suffix = "_update_form"
    redirect_url = "group_list"

    def get_success_url(self) -> str:
        """to what url to return on success"""
        return reverse("edit_group", kwargs={"pk": self.object.pk})


class DeleteGroupView(IsUserAdminMixin, DeleteView):
    """View for deleting groups"""

    model = UserGroups
    success_url = reverse_lazy("group_list")


class EditUserGroupView(IsUserAdminMixin, UpdateView):
    """View for adding user to groups"""

    model = User
    form_class = UpdateUserGroupForm
    template_name = "user/user_group_update_form.html"
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """get context data"""
        context = super().get_context_data(**kwargs)
        context["groups"] = self.object.get_groups()
        return context

    def get_success_url(self) -> str:
        """to what url to return on success"""
        return reverse("edit_user_group", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """how to save data on validation of form"""
        group_id = self.request.POST.get("group")
        group_to_add = UserGroups.objects.get(id=int(group_id))
        edited_user = self.object

        group_to_add.users.add(edited_user)

        return super().form_valid(form)


class DeleteUserFromGroupView(IsUserAdminMixin, DeleteView):
    """Deletes user from group view"""

    model = User
    success_url = reverse_lazy("edit_user_group")

    def post(self, request, *args, **kwargs):
        """post"""
        user = User.objects.get(pk=kwargs["pk"])
        group_to_remove_from = UserGroups.objects.get(pk=kwargs["group_pk"])
        group_to_remove_from.users.remove(user)

        return super().post(request, *args, **kwargs)

    def get_success_url(self) -> str:
        """to what url to return on success"""
        return reverse("edit_user_group", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """rewriting form_valid so that it doesn't deletes user"""
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)


class PermissionListView(ListView):
    """List all user's TablePermissions"""

    model = TablePermission
    template_name = "permissions/list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filter"] = TablePermissionsFilter(self.request.GET)
        return context


class PermissionCreateView(IsUserAdminMixin, CreateView):
    """Create new TablePermission"""

    model = TablePermission
    form_class = TablePermissionForm
    template_name = "permissions/form.html"


class PermissionUpdateView(IsUserAdminMixin, UpdateView):
    """Create new TablePermission"""

    model = TablePermission
    form_class = TablePermissionForm
    template_name = "permissions/form.html"
    pk_url_kwarg = "permission_id"


class PermissionSaveMixin:
    """Permission save mixin"""

    def form_valid(self, form):
        """Save permissions"""
        context = self.get_context_data()
        permission_form = context["permissions_form"]
        with transaction.atomic():
            self.object = form.save()
            permissions = []
            for permission_form in permission_form.forms:
                if permission_form.is_valid():
                    permissions.append(permission_form.save())
            self.object.permissions.set(permissions)
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """get context data"""
        context = super().get_context_data(**kwargs)
        context["permissions_form"] = TablePermissionFormSet(
            self.request.POST or None, queryset=self.object.permissions.all()
        )
        return context


class UserPermissionsEditView(PermissionSaveMixin, UpdateView):
    """Edit user's permissions"""

    model = User
    fields = []
    template_name = "permissions/user_form.html"
    pk_url_kwarg = "user_id"

    def get_success_url(self) -> str:
        return reverse("permission_user_grant", args=[self.object.id])


class UserGroupPermissionEditView(PermissionSaveMixin, UpdateView):
    """Edit group's permissions"""

    model = UserGroups
    fields = []
    template_name = "permissions/group_form.html"
    pk_url_kwarg = "user_group_id"

    def get_success_url(self) -> str:
        return reverse("permission_group_grant", args=[self.object.id])
