from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    role = models.CharField(max_length=150)

    def __str__(self):
        return str(self.role)


class User(AbstractUser):
    role = models.OneToOneField(Role, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.username
