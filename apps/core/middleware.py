import traceback
from django.http import HttpResponse


class PlainTextExceptionMiddleware(object):

    def __init__(self, get_response) -> None:
        self.get_response = get_response


    def __call__(self, request, *args, **kwds):
        response = self.get_response(request)
        if response.status_code != 200:
            traceback.print_exc()
            return HttpResponse(status=500, content=f"{response.status_code} Error")
        return response
