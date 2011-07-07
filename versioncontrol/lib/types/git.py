'''This git implementation is based on the one from Transifex
'''
import os
import os.path

from django.utils.translation import ugettext as _

import versioncontrol.lib.browser as browser
from versioncontrol.lib.support.git import repository, clone
from app.log import (logger)

def need_repo(fn):
    def repo_fn(self, *args, **kw):
        try:
            self.client.status(self.location)
            if self._normalizePath(self.client.root_url_from_path(self.location)) <> self._normalizePath(self.url):
                self._switch_url()
        except pysvn.ClientError:
            self.init_repo()
        return fn(self, *args, **kw)
    return repo_fn 

def need_update(fn):
    def repo_fn(self, *args, **kw):
        self.update()
        return fn(self, *args, **kw)
    return repo_fn

class GitBrowser(browser.RepositoryBrowser):

    def __init__(self, location, url, folder, branch='master', auth=None):
        super(SvnBrowser, self).__init__(location, url, folder, branch, auth)
#        self.login = False
#        self.ssl_trust = False
#        
#        self.revision_update_complete = None
#        self.client = pysvn.Client()
#        self.client.callback_ssl_server_trust_prompt = self._ssl_server_trust_prompt
#        self.client.callback_get_login = self._get_login
#        self.client.callback_notify = self._notify
#        self.client.exception_style = 1
    
    def _notify(self, arg_dict):
        pass
#        msg = None
#        
#        if arg_dict['action'] == pysvn.wc_notify_action.update_completed:
#            self.revision_update_complete = arg_dict['revision']
#            if hasattr(self.revision_update_complete, 'number'):
#                msg = _('At revision %s.') % self.revision_update_complete.number
#            else:
#                msg = _('Completed.') 
#        elif arg_dict['path'] != '' and self.wc_notify_action_map[ arg_dict['action'] ] is not None:
#            if arg_dict['action'] == pysvn.wc_notify_action.update_add:
#                self._send_callback(self.callback_on_file_add,arg_dict['path'])
#            elif arg_dict['action'] == pysvn.wc_notify_action.update_delete:
#                self._send_callback(self.callback_on_file_delete,arg_dict['path'])
#            elif arg_dict['action'] == pysvn.wc_notify_action.update_update:
#                self._send_callback(self.callback_on_file_update,arg_dict['path'])
#            msg = '%s %s' % (self.wc_notify_action_map[ arg_dict['action'] ], os.path.basename(arg_dict['path']))
#
#        if msg:
#            self._send_callback(self.callback_on_action_notify, msg)
            
    @property    
    def _remote_path(self):
        return self.url
#        if self.branch == u'trunk':
#            repo_path = self.branch
#        else:
#            repo_path = "branches/%s" % self.branch
#        return "%s/%s" % (repo_path, self.folder)
    
    def _normalizePath(self, path):
        return os.path.normpath(os.path.normcase(path));
        
    def init_repo(self):
        repo = clone(self._remote_path, self.location)
        repo.branch(self.branch, None)
        repo.checkout(self.branch)
#        logger.debug("init")
#        self._send_callback(self.callback_on_action_notify,_('Initializing repository %s') % self._remote_path)
#
#        try:
#            logger.debug("check path %s" % self.location)
#            if self._normalizePath(self.client.root_url_from_path(self.location)) <> self._normalizePath(self.url):
#                self._switch_url()
#        except pysvn.ClientError, e:
#            logger.debug(e)
#
#        logger.debug("Checkout %s on %s" % (self.url + self._remote_path, self.location))
#        self.client.checkout(self.url + self._remote_path, self._normalizePath(self.location))
#        logger.debug("end")
#        return getattr(self.revision_update_complete,'number',0)

    @need_repo
    def cleanup(self):
        self.client.cleanup(self.location)
        
    @need_repo
    def update(self):
        self.cleanup()
        self._send_callback(self.callback_on_action_notify,_('Updating repository %s') % self._remote_path)        
        self.client.update(self.location)
        return getattr(self.revision_update_complete,'number',0)
#        try:
#        except pysvn.ClientError, e:
#            for message, code in e.args[1]:
#                if code == 155004: # locked
#                    cleanup+=1
#                    if (cleanup>3):
#                        raise
#                    client.cleanup(location)
#                    update(client, location)
#                else:
#                    raise
    
    #@need_update
    
    @need_repo
    def revert(self):
        try:
            self.client.revert([self.location])
        except Exception, e:
            logger.error("Revert %s failed: %s" % (self.location, str(e)))
            pass

    def submit(self, auth, msg):
        self.auth = auth
        logger.debug("Perform submit %s [%s]" % (self.location, msg))
        self._send_callback(self.callback_on_action_notify,_('Checking in'))
        rev = self.client.checkin([self.location], msg.encode('utf-8'), recurse=True, keep_locks=False)
        #Subversion seems to return 0 rather then the actual revision
        self.client.update(self.location)
        return getattr(self.revision_update_complete,'number',0)