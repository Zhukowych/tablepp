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


def get_difference_dict(first_dict: dict, second_dict: dict) -> tuple[dict, dict]:
    """
    Return dicts of keys that changed value
    """
    first_difference_dict = {}
    second_difference_dict = {}
    for key in first_dict:
        if first_dict.get(key) != second_dict.get(key):
            first_difference_dict[key] = first_dict[key]
            second_difference_dict[key] = second_dict[key]
    return first_difference_dict, second_difference_dict
