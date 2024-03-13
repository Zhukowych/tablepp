"""Extent context"""
from django.urls import resolve

def variables(request):
    """Extend context"""

    is_filtering = any(value for value in request.GET.values())
    data = {
        "view_name": resolve(request.path_info).url_name,
        "query": request.GET,
        'is_filtering': is_filtering
    }

    return data
