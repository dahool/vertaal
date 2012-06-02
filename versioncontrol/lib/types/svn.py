# -*- coding: utf-8 -*-
"""Copyright (c) 2009-2012 Sergio Gabriel Teves
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
import os
import os.path

import pysvn

from django.utils.translation import ugettext as _

import versioncontrol.lib.browser as browser
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

class SvnBrowser(browser.RepositoryBrowser):

    wc_notify_action_map = {
        pysvn.wc_notify_action.add: 'A',
        pysvn.wc_notify_action.commit_added: 'A',
        pysvn.wc_notify_action.commit_deleted: 'D',
        pysvn.wc_notify_action.commit_modified: 'M',
        pysvn.wc_notify_action.commit_postfix_txdelta: None,
        pysvn.wc_notify_action.commit_replaced: 'R',
        pysvn.wc_notify_action.copy: 'c',
        pysvn.wc_notify_action.delete: 'D',
        pysvn.wc_notify_action.failed_revert: 'F',
        pysvn.wc_notify_action.resolved: 'R',
        pysvn.wc_notify_action.restore: 'R',
        pysvn.wc_notify_action.revert: 'R',
        pysvn.wc_notify_action.skip: 'skip',
        pysvn.wc_notify_action.status_completed: None,
        pysvn.wc_notify_action.status_external: 'X',
        pysvn.wc_notify_action.update_add: 'A',
        pysvn.wc_notify_action.update_completed: None,
        pysvn.wc_notify_action.update_delete: 'D',
        pysvn.wc_notify_action.update_external: 'X',
        pysvn.wc_notify_action.update_update: 'U',
        pysvn.wc_notify_action.annotate_revision: 'A',
    }
    
    def __init__(self, location, url, folder, branch='trunk', auth=None):
        
        super(SvnBrowser, self).__init__(location, url, folder, branch, auth)
        
        self.login = False
        self.ssl_trust = False
        
        self.revision_update_complete = None
        self.client = pysvn.Client()
        self.client.callback_ssl_server_trust_prompt = self._ssl_server_trust_prompt
        #self.client.callback_get_login = self._get_login
        self.client.callback_notify = self._notify
        self.client.exception_style = 1

        if auth:
            self.set_login(auth)
            
        self.relocated = False
    
    def set_login(self, auth):
        self.client.set_auth_cache(False)
        self.client.set_default_username(auth.get_user())
        self.client.set_default_password(auth.get_password()) 
        
    def _notify(self, arg_dict):
        msg = None
        
        if arg_dict['action'] == pysvn.wc_notify_action.update_completed:
            self.revision_update_complete = arg_dict['revision']
            if hasattr(self.revision_update_complete, 'number'):
                msg = _('At revision %s.') % self.revision_update_complete.number
            else:
                msg = _('Completed.') 
        elif arg_dict['path'] != '' and self.wc_notify_action_map[ arg_dict['action'] ] is not None:
            if arg_dict['action'] == pysvn.wc_notify_action.update_add:
                self._send_callback(self.callback_on_file_add,arg_dict['path'])
            elif arg_dict['action'] == pysvn.wc_notify_action.update_delete:
                self._send_callback(self.callback_on_file_delete,arg_dict['path'])
            elif arg_dict['action'] == pysvn.wc_notify_action.update_update:
                self._send_callback(self.callback_on_file_update,arg_dict['path'])
            msg = '%s %s' % (self.wc_notify_action_map[ arg_dict['action'] ], os.path.basename(arg_dict['path']))

        if msg:
            self._send_callback(self.callback_on_action_notify, msg)
            
    def _ssl_server_trust_prompt(self, trust_data):
        if self.ssl_trust:
            raise browser.BrowserException()
        self.ssl_trust = True
        return True, trust_data['failures'], True 
    
    def _get_login(self, realm, username, may_save):
        if self.login:
            raise browser.BrowserException()
        self.login = True
        return True, str(self.auth.user), str(self.auth.password), False
    
    @property    
    def _remote_path(self):
        if self.branch == u'trunk':
            repo_path = self.branch
        else:
            repo_path = "branches/%s" % self.branch
        return "%s/%s" % (repo_path, self.folder)
    
    def _switch_url(self):
        current_url = self.client.root_url_from_path(self.location)

        self._send_callback(self.callback_on_action_notify,
                            _('URL has changed. Relocate from %(prior)s to %(actual)s')
                                             % {'prior': current_url,
                                                'actual': self.url})
        
        self.client.relocate(current_url, self.url, self.location)
    
    def _normalizePath(self, path):
        return os.path.normpath(os.path.normcase(path));
        
    def init_repo(self):
        logger.debug("init")
        self._send_callback(self.callback_on_action_notify,_('Initializing repository %s') % self._remote_path)

        try:
            logger.debug("check path %s" % self.location)
            if self._normalizePath(self.client.root_url_from_path(self.location)) <> self._normalizePath(self.url):
                self._switch_url()
        except pysvn.ClientError, e:
            logger.debug(e)

        logger.debug("Checkout %s on %s" % (self.url + self._remote_path, self.location))
        try:
            self.client.checkout(self.url + self._remote_path, self._normalizePath(self.location))
        except pysvn.ClientError, e:
            for message, code in e.args[1]:
                if code == 155000: # relocate
                    logger.debug("Must relocate")
                    self._switch_url()
                    self.update()
                else:
                    raise
        logger.debug("end")
        return getattr(self.revision_update_complete,'number',0)

    @need_repo
    def cleanup(self):
        self.client.cleanup(self.location)
        
    @need_repo
    def update(self):
        self.cleanup()
        self._send_callback(self.callback_on_action_notify,_('Updating repository %s') % self._remote_path)        
        try:
            self.client.update(self.location)
        except pysvn.ClientError, e:
            for message, code in e.args[1]:
                if code == 155000: # relocate
                    logger.debug("Must relocate")
                    self._switch_url()
                    self.client.update(self.location)
                elif code == 155004: # locked
                    self.cleanup()
                    self.client.update(self.location)
                else:
                    raise
        return getattr(self.revision_update_complete,'number',0)

    @need_repo
    def revert(self):
        try:
            self.client.revert([self.location])
        except Exception, e:
            logger.error("Revert %s failed: %s" % (self.location, str(e)))
            pass

    def submit(self, auth, files, msg):
        if auth:
            self.set_login(auth)
        logger.debug("Perform submit %s (%s) [%s]" % (self.location, self.files, msg))
        self._send_callback(self.callback_on_action_notify,_('Checking in'))
        try:
            if files:
                rev = self.client.checkin(files, msg.encode('utf-8'), recurse=True, keep_locks=False)
            else:
                rev = self.client.checkin([self.location], msg.encode('utf-8'), recurse=True, keep_locks=False)
        except:
            raise
        if rev and hasattr(rev, 'number'):
            rvn = getattr(self.revision_update_complete,'number', 0)
            if rvn > 0: return rvn
        #Subversion seems to return 0 rather then the actual revision
        self.client.update(self.location)
        return getattr(self.revision_update_complete,'number',0)
