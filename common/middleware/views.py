from django.http import HttpResponseForbidden, HttpResponseNotFound,\
    HttpResponseServerError
from django.template import RequestContext, loader, Context
from django.utils.encoding import smart_str
from django.conf import settings
from django.views.decorators.csrf import requires_csrf_token

def forbidden(request, template_name='403.html'):
    """Default 403 handler"""
    t = loader.get_template(template_name)
    return HttpResponseForbidden(t.render(RequestContext(request)))

def unavailable(request, template_name='503.html'):
    """Default 503 handler"""
    t = loader.get_template(template_name)
    return HttpResponseForbidden(t.render(RequestContext(request)))

@requires_csrf_token
def not_found(request, exception, template_name='404.html'):

    try:
        tried = exception.args[0]['tried']
    except (IndexError, TypeError):
        tried = []
    else:
        if not tried:
            tried = ''

    t = loader.get_template(template_name)
    c = RequestContext(request, {
        'request_path': request.path_info[1:],
        'reason': smart_str(exception, errors='replace'),
        'settings': settings,
    })
    return HttpResponseNotFound(t.render(c))
    
@requires_csrf_token
def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context: None
    """
    t = loader.get_template(template_name) # You need to create a 500.html template.
    return HttpResponseServerError(t.render(RequestContext(request)))
