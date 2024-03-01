"""
Command to safely migrate static models as well as dynammic
"""
from django.core.management.base import BaseCommand
from table.utils.utils import migrate


class Command(BaseCommand):
    """Safe sync command"""

    help = "safely migrate static and dynammic models"

    def handle(self, *args, **options):
        """Handle command execution"""
        migrate()
  
