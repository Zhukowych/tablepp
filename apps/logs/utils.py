"""Utils"""
from django.contrib.contenttypes.models import ContentType
from logs.models import Logs


def log(user, table, object_id, message, description=None):
    """Log change in db"""
    content_type = ContentType.objects.get_for_model(table.get_model())
    Logs.objects.create(
        user=user,
        content_type=content_type,
        object_id=object_id,
        message=message,
        description=description if description else message
    )
