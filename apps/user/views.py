from typing import Any
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import User, Role


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
