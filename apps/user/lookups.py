"""ajax lookups from user app"""

from ajax_select import register, LookupChannel
from .models import User, UserGroups


@register("user")
class UserLookup(LookupChannel):
    """UserLookup"""

    model = User

    def get_query(self, q, request):
        return self.model.objects.filter(username__icontains=q).order_by("username")[
            :50
        ]

    def format_item_display(self, item):
        return "<span class='tag'>%s</span>" % item.username


@register("group_name")
class UserGroupLookup(LookupChannel):
    """UserLookup"""

    model = UserGroups

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q).order_by("name")[:50]

    def format_item_display(self, item):
        return "<span class='tag'>%s</span>" % item.name
