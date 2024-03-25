# pylint: disable=E0307
"""Models for user app"""
from __future__ import annotations
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """Role model"""

    role = models.CharField(max_length=150)

    def __str__(self):
        return self.role

    def get_absolute_url(self):
        """get absolute url"""
        return reverse("role_list")


class User(AbstractUser):
    """User model"""

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    permissions = models.ManyToManyField("TablePermission")
    is_staff = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def get_groups(self):
        """Returns a list of groups in which user exists"""
        return UserGroups.objects.all().filter(users=self)

    def get_groups_to_add(self):
        """Returns a list of groups in which user doesn't exist"""
        return UserGroups.objects.all().exclude(users=self)

    def get_absolute_url(self):
        """get absolute url"""
        return reverse("user_list")

    def has_permission(self, operation: TablePermission.Type, object) -> bool:
        """Return has permission of that operation with accept status"""
        if self.is_superuser:
            return True

        content_type = ContentType.objects.get_for_model(object)
        permissions = self.permissions.filter(
            object_id=object.id, operation=operation, content_type=content_type
        )

        if permissions.exists():
            return permissions.first().accept

        group_permissions = [
            group.permissions.filter(
                content_type=content_type, object_id=object.id, operation=operation
            )
            for group in self.user_groups.all()
        ]

        for group_permission in group_permissions:
            if group_permission.exists():
                return group_permission.first().accept

        if content_type.model == "table":
            return False
        return True


class UserGroups(models.Model):
    """UserGroups model"""

    name = models.CharField(max_length=150, unique=True)
    users = models.ManyToManyField(User, related_name="user_groups")
    permissions = models.ManyToManyField("TablePermission")

    class META:
        """META class"""

        db_name = "user_groups"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """get absolute url"""
        return reverse("group_list")


class TablePermission(models.Model):
    """Permission model"""

    class Type(models.IntegerChoices):
        """Response of permissions"""

        ACCEPT = 0, _("Accept")
        REJECT = 1, _("Reject")

    class Operation(models.IntegerChoices):
        """Type of permission"""

        READ = 0, _("Read")
        WRITE = 1, _("Write")
        DELETE = 2, _("Delete")

    type = models.IntegerField(choices=Type, null=True)
    operation = models.IntegerField(choices=Operation)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey("content_type", "object_id")

    @property
    def target_name(self) -> str:
        """Return name of target object (Table or Column)"""
        if self.content_type.model == "table":
            return _("Table")
        elif self.content_type.model == "column":
            return _("Column")
        raise ValueError("Permission cannot be applied to other models")

    @property
    def accept(self) -> bool:
        """Return True if permission is of accept type"""
        return True if self.type == TablePermission.Type.ACCEPT else False

    def get_absolute_url(self) -> str:
        """Return url to object's page"""
        return reverse("permission_edit", args=[self.id])
