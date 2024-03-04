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

    def __str__(self):
        return self.username

    def get_groups(self):
        return UserGroups.objects.all().filter(users=self)

    def get_absolute_url(self):
        return reverse("user_list")

<<<<<<< HEAD
    def get_groups(self):
        return UserGroups.objects.all().filter(users=self)

    def get_absolute_url(self):
        return reverse("user_list")

=======
>>>>>>> 38d950d (own UserGroups model)

class UserGroups(models.Model):
    name = models.CharField(max_length=150, unique=True)
    users = models.ManyToManyField(User, related_name="user_groups")

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

    response = models.IntegerField(choices=Type)
    operation = models.IntegerField(choices=Operation)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey("content_type", "object_id")

