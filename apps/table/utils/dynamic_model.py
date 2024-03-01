"""Dynamic model"""

from django.urls import reverse


class DynamicModelMixin:
    """Mixin class for dynamic models"""

    table = None

    def get_absolute_url(self) -> str:
        """Return url to Table edit page"""
        return reverse('object-edit', kwargs={'table_id': self.table.id, 
                                              'object_id': self.pk})
