"""Forms in logs app"""
import django_filters

from django.contrib.contenttypes.models import ContentType

from ajax_select.fields import AutoCompleteSelectWidget
from core.forms import BaseFilterSet
from logs.models import Logs
from user.models import User


class LogFilter(BaseFilterSet):
    """Log filter"""

    class Meta:
        """Filter settings"""
        model = Logs
        fields = ['user']

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all(),
                                            widget=AutoCompleteSelectWidget("user"))
    table = django_filters.ModelChoiceFilter(queryset=User.objects.all(), label="Table",
                                            widget=AutoCompleteSelectWidget("table"),
                                            method="filter_by_table")
    object_id = django_filters.NumberFilter()

    def filter_by_table(self, queryset, _, value):
        """Filter by table"""
        content_type = ContentType.objects.get(model=value.slug)
        return queryset.filter(content_type=content_type)
