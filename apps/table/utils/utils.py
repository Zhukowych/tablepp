"""Utils for dynamic tables migration"""
from django.core.management import call_command

from table.models import Table


def migrate():
    """
    Migrate dynamic tables changes (creation, deletion altering) 
    to db
    """

    # load all tables models so syncdb knows about them
    for table in Table.objects.all():
        table.get_model()

    call_command("makemigrations", interactive=False)
    call_command("migrate", interactive=False)
