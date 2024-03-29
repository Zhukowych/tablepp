"""urls module"""

from django.urls import path
from .views import (
    UserLoginView,
    UsersListView,
    AddUserView,
    UpdateUserView,
    UserDeleteView,
    RoleListView,
    AddRoleView,
    UpdateRoleView,
    RoleDeleterView,
    GroupListView,
    AddGroupView,
    UpdateGroupView,
    DeleteGroupView,
    EditUserGroupView,
    DeleteUserFromGroupView,
    PermissionListView,
    UserPermissionsEditView,
    UserGroupPermissionEditView,
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("<int:pk>/edit/", UpdateUserView.as_view(), name="update_user"),
    path("<int:pk>/delete/", UserDeleteView.as_view(), name="delete_user"),
    path("login/", UserLoginView.as_view(), name="login_page"),
    path("logout/", LogoutView.as_view(next_page="/login/"), name="logout"),
    path("list/", UsersListView.as_view(), name="user_list"),
    path("list/add/", AddUserView.as_view(), name="add_user"),
    path("<int:pk>/edit/", UpdateUserView.as_view(), name="update_user"),
    path("<int:pk>/delete/", UserDeleteView.as_view(), name="delete_user"),
    path("login/", UserLoginView.as_view(), name="login_page"),
    path("logout/", LogoutView.as_view(next_page="/login/"), name="logout"),
    path("list/", UsersListView.as_view(), name="user_list"),
    path("add/", AddUserView.as_view(), name="add_user"),
    path("role/", RoleListView.as_view(), name="role_list"),
    path("role/add/", AddRoleView.as_view(), name="add_role"),
    path("role/<int:pk>/edit/", UpdateRoleView.as_view(), name="update_role"),
    path("role/<int:pk>/delete/", RoleDeleterView.as_view(), name="delete_role"),
    path("groups/", GroupListView.as_view(), name="group_list"),
    path("groups/add/", AddGroupView.as_view(), name="add_group"),
    path("groups/<int:pk>/edit/", UpdateGroupView.as_view(), name="edit_group"),
    path("groups/<int:pk>/delete/", DeleteGroupView.as_view(), name="delete_group"),
    path("<int:pk>/edit/groups/", EditUserGroupView.as_view(), name="edit_user_group"),
    path(
        "<int:pk>/edit/groups/<int:group_pk>/delete/",
        DeleteUserFromGroupView.as_view(),
        name="delete_user_from_group",
    ),
    path("permissions/", PermissionListView.as_view(), name="permission_list"),
    path(
        "<int:user_id>/permissions/",
        UserPermissionsEditView.as_view(),
        name="permission_user_grant",
    ),
    path(
        "groups/<int:user_group_id>/permissions/",
        UserGroupPermissionEditView.as_view(),
        name="permission_group_grant",
    ),
]
