from __future__ import annotations
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    role = models.CharField(max_length=150)

    def __str__(self):
        return self.role

    def get_absolute_url(self):
        return reverse("role_list")


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    permissions = models.ManyToManyField("TablePermission")

    def __str__(self):
        return self.username

    def get_groups(self):
        return UserGroups.objects.all().filter(users=self)

    def get_absolute_url(self):
        return reverse("user_list")

    def get_groups(self):
        return UserGroups.objects.all().filter(users=self)

    def get_absolute_url(self):
        return reverse("user_list")

    def has_permission(self, operation: TablePermission.Type, object) -> bool:
        """Return has permission of that operation with accept status"""
        permissions = self.permissions.filter(object=object, operation=operation)
        if permissions.exists():
            return permissions.first().accept

        group_permissions = [ group.permissions for group in self.user_groups ]

        for group_permission in group_permissions:
            if group_permission.exists():
                return group_permission.first().accept

        return False

class UserGroups(models.Model):
    name = models.CharField(max_length=150, unique=True)
    users = models.ManyToManyField(User, related_name="user_groups")
    permissions = models.ManyToManyField("TablePermission")

    class META:
        db_name = "user_groups"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
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
