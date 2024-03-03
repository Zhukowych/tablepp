from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    role = models.CharField(max_length=150)

    def __str__(self):
        return self.role

    def get_absolute_url(self):
        return reverse("role_list")


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("user_list")


class UserGroups(models.Model):
    name = models.CharField(max_length=150, unique=True)
    users = models.ManyToManyField(User, related_name="user_groups")

    class META:
        db_name = "user_groups"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("group_list")
