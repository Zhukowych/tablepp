"""mixins"""
from json import JSONEncoder

from django.shortcuts import redirect
from django.contrib import messages


class IsUserAdminMixin:
    """checks whether user is super admin"""

    redirect_url = "user_list"

    def dispatch(self, request, *args, **kwargs):
        """disaptach over"""
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, "You have no permission to access this page")
            return redirect(self.redirect_url)


class BaseJSONEncoder(JSONEncoder):
    """Extended encoder, uses repr of object
    if can't convert it to JSON"""

    def default(self, obj):
        return repr(obj)
