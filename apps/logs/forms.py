"""Forms in logs app"""
import django_filters
from django.contrib.contenttypes.models import ContentType

from logs.models import Logs


class LogFilter(django_filters.FilterSet):
    """Log filter"""

    class Meta:
        """Filter settings"""
        model = Logs
        fields = ['user', 'content_type', 'object_id']

    content_type = django_filters.ModelChoiceFilter(queryset=Logs.objects.none())
