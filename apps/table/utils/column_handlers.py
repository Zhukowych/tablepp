"""
A set of classes for converting Columns to 
djnago classes
"""
from abc import ABC, abstractmethod
from django.db.models import Field, IntegerField
from django.utils.translation import gettext_lazy as _


class ColumnHandler(ABC):
    """
    ColumnHandler is a class for converting table.models.Column 
    to django fields
    """

    def __init__(self, name: str, slug: str, settings: dict) -> None:
        """Initialize ColumnHandler"""
        self.name = name
        self.slug = slug
        self.settings = settings

    @abstractmethod
    def get_model_field(self) -> Field:
        """Return model field for column"""

    def get_kwargs(self) -> tuple[list, dict]:
        """
        Return default kwargs of django model field
        """
        return {'null': True, 'blank': True}


class IntegerColumnHandler(ColumnHandler):
    """Handler for IntegerColumn"""

    def get_model_field(self) -> Field:
        kwargs = self.get_kwargs()
        return IntegerField(_(self.name), **kwargs) 

