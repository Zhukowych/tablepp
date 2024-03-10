"""Ajax lookups for table app"""
from ajax_select import register, LookupChannel
from table.models import Table, Column


@register('table')
class TableLookup(LookupChannel):
    """Table Lookup"""

    model = Table

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q).order_by('name')[:50]

    def format_item_display(self, table):
        """format on display"""
        return "<span>%s</span>" % table.name


@register('column')
class ColumnLookup(LookupChannel):
    """Column Lookup"""

    model = Column

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q).order_by('name')[:50]

    def format_item_display(self, column):
        """format on display"""
        return "<span>%s</span>" % column.name
