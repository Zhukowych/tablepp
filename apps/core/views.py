from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def handle_404(request, exception):
    return HttpResponse(status=404, content="Not Found")


def handle_500(request, exception):
    return HttpResponse(status=404, content="Internal Server Error")
