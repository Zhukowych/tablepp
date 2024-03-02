from typing import Any

from django.shortcuts import redirect
from django.urls import reverse


class CheckAuthenticated:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request, *args: Any, **kwds: Any) -> Any:

        if not request.user.is_authenticated and request.path != "/login/":
            return redirect(reverse("login_page"))

        return self.get_response(request)
