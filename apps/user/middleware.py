"""Middleware """

from typing import Any

from django.shortcuts import redirect
from django.urls import reverse


class CheckAuthenticated:
    """doesn't let unautenticated user's to visit pages"""

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request, *args: Any, **kwds: Any) -> Any:
        if request.path.startswith('/static/'):
            return self.get_response(request)

        if not request.user.is_authenticated and request.path != "/user/login/":
            return redirect(reverse("login_page"))

        return self.get_response(request)
