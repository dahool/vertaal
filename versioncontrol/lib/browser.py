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

from versioncontrol.lib.types import BROWSER_TYPES
from common.utils.commands import *

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

class AuthException(Exception):
    pass
        
class BrowserAuth(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password
        
    def get_user(self):
        return str(self.user)
    
    def get_password(self):
        return str(self.password)
    
class RepositoryBrowserFactory(object):
    def get_browser(type):
    	# this method must not have 'self' param
        mod_name, obj_name = BROWSER_TYPES[type]        
        obj = getattr(__import__(mod_name, {}, {}, ['']), obj_name)
        return obj
    get_browser = Callable(get_browser)
        
class RepositoryBrowser(object):

    def __init__(self, location, url, folder, branch, auth):    
        """ initialize the browser instance

        available callbacks are:
        
        callback_on_action_notify ( arg ): every taken action
        callback_on_file_delete ( absolute_filename ): on file delete
        callback_on_file_add ( absolute_filename ): on file add
        callback_on_file_update ( absolute_filename ): on file update
        """
        # remote url
        if url.endswith('/'):
            self.url = url  
        else:
            self.url = url + "/"
        # remote branch
        self.branch = branch
        # remote folder
        self.folder = folder
        # local path (destination)
        self.location = location
        self.auth = auth

        # init callbacks
        self.callback_on_action_notify = None
        self.callback_on_file_delete = None
        self.callback_on_file_add = None
        self.callback_on_file_update = None     
            
    def init_repo(self):
        """ initialize repository
        """
        
    def cleanup(self):
        """ cleanup any pending operation
        """
        
    def update(self):
        """ perform update
        """

    def submit(self, auth, files, msg):
        """ commit the files
            requires a BrowserAuth instance
        """

    def revert(self, path):
        """ revert
        """
        
    def _send_callback(self, callback, param):
        if callback:
            callback(param)
                
class BrowserException(Exception):
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)
    
class _Repo(object):
    def __init__(self, path):
        self.path = os.path.realpath(path)

        if not os.path.isdir(self.path) or not os.path.exists(self.path):
            raise BrowserException("repository %s not found" % self.path)

    def run(self, *args, **kwargs):
        return run_command(cwd=self.path, *args, **kwargs)     
