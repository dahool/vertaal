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
import string

from django.utils.translation import ugettext as _
from django.utils.encoding import smart_text
import versioncontrol.lib.browser as browser
from versioncontrol.lib.support import svnclient

import logging
logger = logging.getLogger('vertaal.vcs')

def need_repo(fn):
    def repo_fn(self, *args, **kw):
        try:
            info = self.client.info()
            if self.client.parseurl(info['url']) <> self.client.parseurl(self.url):
                self._switch_url()
        except svnclient.ClientError:
            self.init_repo()
        return fn(self, *args, **kw)
    return repo_fn 

def need_update(fn):
    def repo_fn(self, *args, **kw):
        self.update()
        return fn(self, *args, **kw)
    return repo_fn

def encode_text(text, encoding='utf-8'):
    xv = filter(lambda x: x in string.printable, text)
    return smart_text(xv, encoding=encoding)    
#    try:
#        return smart_text(text, encoding=encoding)
#    except UnicodeDecodeError:
#        xv = filter(lambda x: x in string.printable, text)
#        return smart_text(xv, encoding=encoding)    

class SubversionBrowser(browser.RepositoryBrowser):

    update_completed = 'update'
    
    relocate_error_msg = 'is already a working copy for a different URL'            
    
    def __init__(self, location, url, folder, branch='trunk', auth=None):
        super(SubversionBrowser, self).__init__(location, url, folder, branch, auth)
        
        self.client = svnclient.Client(location=self._normalizePath(location))
        self.client.set_trust_server_cert(True)

        if auth:
            self.set_login(auth)
            
        self.relocated = False
    
    def set_login(self, auth):
        self.client.set_username(auth.get_user())
        self.client.set_password(auth.get_password()) 
        
    def _notify(self, arg_dict):
        msg = None
        try:
            logger.debug(arg_dict)
            if arg_dict['action'] == self.update_completed:
                msg = _('At revision %s.') % arg_dict['revision']
            elif arg_dict.has_key('path'):
                if arg_dict['action'] == svnclient.notify_action.added:
                    self._send_callback(self.callback_on_file_add,arg_dict['path'])
                elif arg_dict['action'] == svnclient.notify_action.deleted:
                    self._send_callback(self.callback_on_file_delete,arg_dict['path'])
                elif arg_dict['action'] == svnclient.notify_action.updated:
                    self._send_callback(self.callback_on_file_update,arg_dict['path'])
                elif arg_dict['action'] == svnclient.notify_action.replaced:
                    self._send_callback(self.callback_on_file_update,arg_dict['path'])                    
                msg = '%s %s' % (arg_dict['action'], os.path.basename(arg_dict['path']))
        except KeyError:
            logger.error(arg_dict)
            
        if msg:
            self._send_callback(self.callback_on_action_notify, msg)
    
    def _parse_event_list(self, eventList):
        for event in eventList:
            self._notify(event)
    
    @property    
    def _remote_path(self):
        if self.branch == u'trunk':
            repo_path = self.branch
        else:
            repo_path = "branches/%s" % self.branch
        return "%s/%s" % (repo_path, self.folder)
    
    def _switch_url(self):
        current_url = self.client.parseurl(self.client.get_remote_url())
        new_url = self.client.parseurl(self.url)

        self._send_callback(self.callback_on_action_notify,
                            _('URL has changed. Relocate from %(prior)s to %(actual)s')
                                             % {'prior': current_url,
                                                'actual': new_url})
        
        self.client.relocate(current_url, new_url)
    
    def _normalizePath(self, path):
        return os.path.normpath(os.path.normcase(path));
        
    def init_repo(self):
        logger.debug("init")
        self._send_callback(self.callback_on_action_notify,_('Initializing repository %s') % self._remote_path)

        try:
            logger.debug("check path %s" % self.location)
            info = self.client.info()
            if self.client.parseurl(info['url']) <> self.client.parseurl(self.url):
                self._switch_url()
        except svnclient.ClientError, e:
            logger.debug(e)

        logger.debug("Checkout %s on %s" % (self.url + self._remote_path, self.location))
        rev = 0
        try:
            rev, eventList = self.client.checkout(url = self.url + self._remote_path)
            self._parse_event_list(eventList)
        except svnclient.ClientError, e:
            # TODO handle relocate error more effectivly
            if e.message.find(self.relocate_error_msg):
                logger.debug("Must relocate")
                self._switch_url()
                rev = self.update()
            else:
                raise
        logger.debug("end")
        self._notify({'action': self.update_completed, 'revision': rev})
        return rev

    @need_repo
    def cleanup(self):
        self.client.cleanup()
        
    @need_repo
    def update(self):
        self.cleanup()
        self._send_callback(self.callback_on_action_notify,_('Updating repository %s') % self._remote_path)        
        rev = 0
        try:
            rev, eventList = self.client.update(force=True)
            self._parse_event_list(eventList)
        except svnclient.ClientError, e:
            #if self._checkerror(e, 155000): # relocate
            logger.debug("Must relocate")
            self._switch_url()
            rev, eventList = self.client.update(force=True)
            self._parse_event_list(eventList)
        self._notify({'action': self.update_completed, 'revision': rev})            
        return rev

    @need_repo
    def revert(self, path=None):
        try:
            if path is not None:
                self.client.revert([path])    
            else:
                filelist = self.client.status()
                if filelist is not None:
                    files = []
                    for event in filelist:
                        files.append(event['path'])
                    self.client.revert(files)
        except Exception, e:
            logger.error("Revert %s failed: %s" % (self.location, str(e)))
            pass

    def _checkin(self, msg):
        filelist = self.client.status()
        files = []
        if filelist is not None:
            for event in filelist:
                if event['action'] == svnclient.notify_action.noadded:
                    files.append(event['path'])
            if len(files) > 0:
                self.client.add(files)
        rev = self.client.commit(message=encode_text(msg))
        return rev
        
    def submit(self, auth, files, msg):
        if auth:
            self.set_login(auth)
        logger.debug("Perform submit %s (%s) [%s]" % (self.location, files, msg))
        self._send_callback(self.callback_on_action_notify,_('Checking in'))
        rev = 0
        try:
            rev = self._checkin(msg)
        except svnclient.ClientError, e:
            logger.debug(str(e))
            logger.warn(str(e))
            self.cleanup()
            try:
                rev = self._checkin(msg)
            except:
                raise
        except:
            raise
        self._notify({'action': self.update_completed, 'revision': rev})            
        return rev
