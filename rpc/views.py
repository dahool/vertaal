import base64
import datetime
from django_xmlrpc.decorators import xmlrpc
from common.modelparser import parse

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from rpc.models import RpcSession
from files.models import *
from files.lib.handlers import handle_text_file
from projects.models import Project
from releases.models import Release
from teams.models import Team
from rpc.log import logger
from rpc.utils import generate_token

class verify_token:
    def __init__(self, fn):
        self.fn = fn
    
    def __call__(self, *args, **kw):
        token = args[0]
        try:
            r = RpcSession.objects.get(token=token)
        except:
            return '[ERR001]: %s' % _('Session invalid or expired.')
        else:
            dff = datetime.datetime.now() - r.created
            if dff.seconds > 3600:
                # remove the session as we are here
                r.delete()
                return '[ERR001]: %s' % _('Session invalid or expired.')
        kw['user'] = r.user
        return self.fn(*args[1:], **kw)
    
@xmlrpc('login')
def do_login(user, password):
    '''perfom login
    params:
        username: string
        password: string (plaintext)
    returns:
        token if success
    '''
    try:
        u = User.objects.get(username=user)
    except:
        return '[ERR000]: %s' % _('Invalid.')
    else:
        if not u.check_password(password):
            return '[ERR000]: %s' % _('Invalid.')
    token = '%s+%s' % (user,generate_token(user + password))
    RpcSession.objects.create(user=u, token=token)
    return token

@xmlrpc('logout')
def do_logout(token):
    try:
        r = RpcSession.objects.get(token=token)
        r.delete()
    except:
        pass
    return 'OK'
 
@xmlrpc('list_projects')
def do_project_list():
    '''<pre>get the projects list
    params:
        None
    returns
        list
    </pre>
    '''
    return parse(Project.objects.filter(enabled=True, read_only=False), exclude=['repo_user','repo_pwd'])

@xmlrpc('list_releases')
def do_release_list(project=None):
    '''get the releases list
    params:
        (optional) projectId
    returns
        list
    '''
    if project:
        r = Release.objects.filter(project__id=project, enabled=True)
    else:
        r = Release.objects.filter(enabled=True)
    return parse(r)

@xmlrpc('list_teams')
def do_team_list(project):
    '''get team list for a given project
    params:
        project id
    returns
        list
    '''
    return parse(Team.objects.select_related('language').filter(project__id=project))

@xmlrpc('list_files')
def do_get_files(release, language):
    '''return file list for given release and language
    params:
        release id
        language id
    returns
        list
    '''
    return parse(POFile.objects.select_related('component').filter(
                                                                release__id=release,
                                                                language__id=language),
                                                                force=['locks'])
@xmlrpc('get_user')
def do_get_user(user_id):
    return parse(User.objects.get(id=user_id),exclude=['password','email','last_login','date_joined'])

@xmlrpc('upload_file')
@verify_token
def do_upload_file(file_id, data, user):
    logger.debug("Upload file %s by %s" % (file_id, user))
    try:
        file = POFile.objects.get(id=file_id,
                                  locks__owner=user)
    except POFile.DoesNotExist:
        # file is not locked by the user
        logger.debug("Not locked")
        return '[ERR101]: %s' % _('File is not locked.')
    except Exception, e:
        logger.error(e)
        return '[ERR999]: %s' % _('Failed: [%s].') % e 
    else:
        handle_text_file(file, base64.b64decode(data).decode('utf-8'), user)
    return 'OK'

@xmlrpc('get_file_content')
def do_get_file(file_id):
    file = POFile.objects.get(id=file_id)
    content = file.handler.get_content(True)
    return base64.b64encode(content)