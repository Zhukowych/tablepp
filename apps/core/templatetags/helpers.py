"""Global templatetags"""
from django_jinja import library
from jinja2 import pass_context
from markupsafe import Markup

@pass_context
def insert_on_name(context, name: str, text: str):
    """Return string if currenty on url with specified name"""    
    if name == context['view_name']:
        return Markup(text)
    return Markup("")

def display_errors(field):
    """Render errors of form"""
    html = ""
    for error in field.errors:
        html += f"<span class='error'>{error}</span>"
    return Markup(html)


@library.render_with("paginator.html")
def paginator(page_object):

    return {'page_obj': page_object}
