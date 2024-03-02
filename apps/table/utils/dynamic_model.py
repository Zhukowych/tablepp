"""Dynamic model"""
from typing import Any
from django.urls import reverse


class DynamicModelMixin:
    """Mixin class for dynamic models"""

    table = None

    def get_absolute_url(self) -> str:
        """Return url to Table edit page"""
        return reverse('object-edit', kwargs={'table_id': self.table.id,
                                              'object_id': self.pk})

    def get_value_of(self, column) -> Any:
        """Get value of column at this object"""
        return getattr(self, column.slug)


class DynamicModelFormMixin:
    """Mixin class for ModelForm that uses dynamic model"""



class DynamicModelFilterSetMixin:
    """Mixin class for FilterSet that works with dynamic model"""
