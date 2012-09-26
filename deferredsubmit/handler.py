from deferredsubmit.models import POFileSubmitDeferred
from django.conf import settings
from django.utils.encoding import smart_unicode
from versioncontrol.manager import SubmitClient
import traceback
from app.log import (logger)

deferred_enabled = getattr(settings,'DEFERRED_SUBMIT', False)

def add_submit(filesubmit, user, repo_user, repo_pwd, msg):
    try:
        podef = POFileSubmitDeferred.objects.get(filesubmit=filesubmit)
        podef.repo_user = repo_user
        podef.repo_pwd = repo_pwd
        podef.user = user
        podef.message = msg
        podef.save()
    except POFileSubmitDeferred.DoesNotExist:
        podef = POFileSubmitDeferred.objects.create(filesubmit=filesubmit, user=user, repo_user=repo_user, repo_pwd=repo_pwd, message=msg)
    filesubmit.locked = True
    filesubmit.save()
    
def add_submits(submits, user, repo_user, repo_pwd, msg):
    for submit in submits:
        add_submit(submit, user, repo_user, repo_pwd, msg)

class UserFiles:
    user = None
    repo_user = None
    repo_pwd = None
    files = []
    messages = set()
    
    def __init__(self, user, repo_user, repo_pwd):
        self.user = user
        self.repo_user = repo_user
        self.repo_pwd = repo_pwd
    
    def add_message(self, msg):
        if msg and len(msg)>0:
            self.messages.add(msg)
    
    @property
    def message(self):
        return "\n".join(self.messages)
        
def process_queue():
    from django.utils.translation import ugettext as _
    count = 0
    erc = 0
    submits = {}
    # group by project and user
    files = POFileSubmitDeferred.objects.get_ordered()
    for sf in files:
        project = sf.filesubmit.pofile.release.project.slug
        userkey = sf.user.username
        if not submits.has_key(project):
            submits[project] = {userkey: UserFiles(sf.user, sf.repo_user, sf.repo_pwd)}
        elif not submits[project].has_key(userkey):
            submits[project][userkey] = UserFiles(sf.user, sf.repo_user, sf.repo_pwd)
        submits[project][userkey].files.append(sf.filesubmit)
        submits[project][userkey].add_message(sf.message)
        sf.delete()
        
    for project in submits.values():
        for userfile in project.values():
            c = SubmitClient(userfile.files,
                             userfile.user,
                             userfile.repo_user,
                             userfile.repo_pwd,
                             userfile.message)
            try:
                count += 1
                c.run()
            except Exception, e:
                erc += 1
                logger.error(e)
                logger.error(traceback.format_exc())
                userfile.user.message_set.create(
                                    message=_("Submit failed. Reason: %s") % smart_unicode(e))
    return {'count': count, 'errors': erc}
