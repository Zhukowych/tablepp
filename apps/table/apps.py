from django.apps import AppConfig


class TableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'table'

    def ready(self):
        from table.models import Table
        for table in Table.objects.all():
            table.get_model()

        for table in Table.objects.all():
            table.register_ajax_lookup()
