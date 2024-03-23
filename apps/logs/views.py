from typing import Any
from django.shortcuts import render

from django.views.generic import ListView, DetailView

from logs.models import Logs
from logs.forms import LogFilter


class LogsListView(ListView):
    """List all logs"""

    model = Logs
    template_name = "log_list.html"
    ordering = ['-id']
    paginate_by = 15

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['filter'] = LogFilter(self.request.GET or None, queryset=Logs.objects.all())
        return context


class LogDetailView(DetailView):

    model = Logs
    pk_url_kwarg = "log_id"
    template_name = "log_detail.html"
