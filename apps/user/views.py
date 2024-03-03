from typing import Any
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import User, Role, UserGroups
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
    fields = ["username", "password", "email", "role"]


class UpdateUserView(UpdateView):
    model = User
    fields = ["username", "password", "email", "role"]
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
        print(context)
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

        # print(UserGroups.objects.get(id=2))

        return render(
            request,
            self.template_name,
            context={"message": "Fuck you, bitch", "object": User},
        )

    def post(self, request, *args, **kwargs):
        return HttpResponse("POST request received!")
