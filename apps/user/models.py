from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    role = models.CharField(max_length = 150)
    
    def __str__(self):
        return self.role

class UserProfile(User):
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)