from django.urls import path, include
from .views import (
    UserProfileDetailView,
    UserLoginView,
    UsersListView,
    AddUserView,
    RoleListView,
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("<int:pk>/", UserProfileDetailView.as_view(), name="user_detail"),
    path("login/", UserLoginView.as_view(), name="login_page"),
    path("logout/", LogoutView.as_view(next_page="/login/"), name="logout"),
    path("list/", UsersListView.as_view(), name="user_list"),
    path("list/add/", AddUserView.as_view(), name="add_user"),
    path("role/", RoleListView.as_view(), name="role_list"),
]
