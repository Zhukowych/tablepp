"""
    Jinja 2 settings
"""
from jinja2 import Environment
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage

from apps.core.templatetags.helpers import insert_on_name
# for more later django installations use:
# from django.templatetags.static import static


def environment(**options):
	env = Environment(**options)
	env.globals.update({
		"static": staticfiles_storage.url,
		"url": reverse,
		"insert_on_name": insert_on_name
	})
	return env 
