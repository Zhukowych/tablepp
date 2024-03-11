"""Extent context"""
from django.urls import resolve

def variables(request):
    """Extend context"""

    data = {
        "view_name": resolve(request.path_info).url_name
    }

    return data
