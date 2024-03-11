from typing import Any
from django.forms import BaseModelForm
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import User, Role
from django.forms import BaseModelForm
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import User, Role, UserGroups
from .forms.form import UpdateUserGroupForm, TablePermissionsFilter, TablePermissionForm, TablePermissionFormSet, UserForm
from .models import User, Role, UserGroups, TablePermission
from .forms.form import UpdateUserGroupForm


class UserProfileDetailView(DetailView):
    model = User
    template_name = "user/user_details.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:

        context = super().get_context_data(**kwargs)
        return context


class UserLoginView(LoginView):
    redirect_authenticated_user = True

    def get_success_url(self) -> str:

        user_pk = self.request.user.pk

        return reverse("user_detail", kwargs={"pk": user_pk})


class UsersListView(ListView):
    model = User
    paginate_by = 10


class RoleListView(ListView):
    model = Role
    paginate_by = 10


class AddUserView(CreateView):
    model = User
    form_class = UserForm

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        user = form.save(commit=False)
        print("debug")
        print(form.cleaned_data)
        print("debug")
        user.password = make_password(form.cleaned_data["password"])
        user.save()

        return super().form_valid(form)


class UpdateUserView(UpdateView):
    model = User
    form_class = UserForm
    template_name_suffix = "_update_form"


class UserDeleteView(DeleteView):
    model = User
    success_url = reverse_lazy("user_list")


class AddRoleView(CreateView):
    model = Role
    fields = ["role"]


class UpdateRoleView(UpdateView):
    model = Role
    fields = ["role"]
    template_name_suffix = "_update_form"


class RoleDeleterView(DeleteView):
    model = Role
    success_url = reverse_lazy("role_list")


class GroupListView(ListView):
    model = UserGroups
    template_name = "user/group_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:

        context = super().get_context_data(**kwargs)
        return context


class AddGroupView(CreateView):
    model = UserGroups
    fields = ["name"]


class UpdateGroupView(UpdateView):
    model = UserGroups
    fields = ["name"]
    template_name_suffix = "_update_form"


class DeleteGroupView(DeleteView):
    model = UserGroups
    success_url = reverse_lazy("group_list")


class EditUserGroupView(View):

    form_class = UpdateUserGroupForm
    template_name = "user/user_group_update_form.html"

    def get(self, request, *args, **kwargs):

        print(request.user.get_groups())
        # print(UserGroups.objects.get(id=2))
        print(request.user.get_groups())

        return render(
            request,
            self.template_name,
            context={"message": "Fuck you, bitch", "object": User},
        )

    def post(self, request, *args, **kwargs):
        return HttpResponse("POST request received!")


class PermissionListView(ListView):
    """List all user's TablePermissions"""

    model = TablePermission
    template_name = "permissions/list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['filter'] = TablePermissionsFilter(self.request.GET)
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


class PermissionSaveMixin:
    """Permission save mixin"""

    def form_valid(self, form):
        """Save permissions"""
        context = self.get_context_data()
        permission_form = context['permissions_form']
        with transaction.atomic():
            self.object = form.save()
            permissions = []
            for permission_form in permission_form.forms:
                if permission_form.is_valid():
                    permissions.append(permission_form.save())
            self.object.permissions.set(permissions)
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['permissions_form'] = TablePermissionFormSet(self.request.POST or None,
                                                             queryset=self.object.permissions.all())
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
    template_name = "permissions/user_form.html"
    pk_url_kwarg = "user_group_id"

    def get_success_url(self) -> str:
        return reverse("permission_group_grant", args=[self.object.id])

class UserPermissionDeleteView(DeleteView):
    """Delete TablePermission view"""
    pass
