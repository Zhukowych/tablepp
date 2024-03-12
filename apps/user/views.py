"""User app views"""

from typing import Any
from django.forms import BaseModelForm
from django.views.generic.detail import DetailView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import User, Role
from core.utils import IsUserAdminMixin
from django.forms import BaseModelForm
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import User, Role, UserGroups
from .forms.form import (
    UpdateUserGroupForm,
    TablePermissionsFilter,
    TablePermissionForm,
    TablePermissionFormSet,
)
from .models import User, Role, UserGroups, TablePermission
from .forms.form import UpdateUserGroupForm


class UserProfileDetailView(DetailView):
    """view for user's info"""

    model = User
    template_name = "user/user_details.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """get context data"""

        context = super().get_context_data(**kwargs)
        return context


class UserLoginView(LoginView):
    """View for login"""

    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        """to what url return a user on success"""

        user_pk = self.request.user.pk

        return reverse("user_detail", kwargs={"pk": user_pk})


class UsersListView(ListView):
    """View for list of users"""

    model = User
    paginate_by = 10


class RoleListView(ListView):
    """View for list of roles"""

    model = Role
    paginate_by = 10


class AddUserView(CreateView):
    """View for creating user's users"""

    model = User
    fields = ["username", "password", "email", "role"]

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """hashes new user's password on validation of form"""
        user = form.save(commit=False)
        user.password = make_password(form.cleaned_data["password"])
        user.save()

        return super().form_valid(form)


class UpdateUserView(UpdateView):
    """View for updating info about user"""

    model = User
    fields = ["username", "password", "email", "role"]
    template_name_suffix = "_update_form"


class UserDeleteView(IsUserAdminMixin, DeleteView):
    """View for deleting user"""

    model = User
    success_url = reverse_lazy("user_list")


class AddRoleView(CreateView):
    """View for adding roles"""

    model = Role
    fields = ["role"]


class UpdateRoleView(UpdateView):
    """View for updating roles name"""

    model = Role
    fields = ["role"]
    template_name_suffix = "_update_form"


class RoleDeleterView(IsUserAdminMixin, DeleteView):
    """View for deleting role"""

    model = Role
    success_url = reverse_lazy("role_list")


class GroupListView(ListView):
    """View for listing groups"""

    model = UserGroups
    template_name = "user/group_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Get context data"""

        context = super().get_context_data(**kwargs)
        return context


class AddGroupView(CreateView):
    """View for adding groups"""

    model = UserGroups
    fields = ["name"]


class UpdateGroupView(UpdateView):
    """View for updating group info"""

    model = UserGroups
    fields = ["name"]
    template_name_suffix = "_update_form"


class DeleteGroupView(IsUserAdminMixin, DeleteView):
    """View for deleting groups"""

    model = UserGroups
    success_url = reverse_lazy("group_list")


class EditUserGroupView(UpdateView):
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


class PermissionCreateView(CreateView):
    """Create new TablePermission"""

    model = TablePermission
    form_class = TablePermissionForm
    template_name = "permissions/form.html"


class PermissionUpdateView(UpdateView):
    """Create new TablePermission"""

    model = TablePermission
    form_class = TablePermissionForm
    template_name = "permissions/form.html"
    pk_url_kwarg = "permission_id"


class UserPermissionsEditView(UpdateView):
    """Edit user's permissions"""

    model = User
    fields = []
    template_name = "permissions/user_form.html"
    pk_url_kwarg = "user_id"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["permissions_form"] = TablePermissionFormSet(self.request.POST or None)
        return context

    def get_success_url(self) -> str:
        return reverse("edit_user_group")


class UserPermissionDeleteView(DeleteView):
    """Delete TablePermission view"""

    pass
