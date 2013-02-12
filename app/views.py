import chunk
import tempfile
import os

from django.shortcuts import render_to_response
from django.template import RequestContext
from common.simplexml import XMLResponse
from common.middleware.exceptions import Http403
from projects.models import Project
from common.view.decorators import *
from django.conf import settings

@render('index.html')
def index(request):
    latest_projects = Project.objects.by_authorized(request.user).order_by('-created')[:settings.SHOW_LATEST_PROJECTS]
    return {'latest_projects': latest_projects}
    
@render('messages.html')
def messages(request):
    return {}

def v2gwelcome(request):
    if request.user.is_authenticated():
        return index(request)
    else:
        return render_to_response("v2g_message.html",
            {}, 
              context_instance = RequestContext(request)) 
    
def get_log(request, file):
    if request.method != 'POST':
        raise Http403
    
    res = {}
    offset = request.POST.get('offset')
    filename = os.path.join(tempfile.gettempdir(), settings.PROJECT_NAME, file, '.log')
    c = chunk.Chunk(file(filename))
    c.seek(offset)
    res['text_HTML'] = c.read()
    res['offset'] = c.tell()
    if os.path.exists(filename + '.end'):
         res['offset']='END'
    return XMLResponse(res)