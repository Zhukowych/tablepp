from django.core.exceptions import PermissionDenied


class IsUserAdminMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
