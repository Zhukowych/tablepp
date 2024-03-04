"""Logs models"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from table.models import Table
from user.models import User


class Logs(models.Model):
    """
    Log entity. Contain data about user's actions on tables or fields.
    """

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey("content_type", "object_id")
    message = models.CharField(max_length=256)
    description = models.CharField(max_length=512)
