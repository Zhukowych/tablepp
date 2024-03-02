from typing import Any
from django.shortcuts import render
from django.views.generic.detail import DetailView, ListView
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import UserProfile


class UserProfileDetailView(DetailView):
    model = UserProfile
    template_name = "user/user_details.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:

        context = super().get_context_data(**kwargs)
        return context


class UserLoginView(LoginView):
    redirect_authenticated_user = True

    def get_success_url(self) -> str:

        user_pk = self.request.user.pk

        return reverse("user_detail", kwargs={"pk": user_pk})


class UsersList(ListView):
    pass
