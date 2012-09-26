# -*- coding: utf-8 -*-
"""Copyright (c) 2012 Sergio Gabriel Teves
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
import time
import shutil

from django.utils.translation import ugettext as _

import versioncontrol.lib.browser as browser
from app.log import (logger)

# This is for test only, is not completed

class FileSystemBrowser(browser.RepositoryBrowser):

    def __init__(self, location, url, folder, branch='', auth=None):
        super(FileSystemBrowser, self).__init__(location, url, folder, branch, auth)
        if self.url.startswith('file://'):
            self.url = self.url[7:]
            
    @property
    def _remote_location(self):
        return os.path.join(self.url, self.branch, self.folder)
        
    def init_repo(self):
        logger.debug("init")
        self._send_callback(self.callback_on_action_notify,_('Initializing repository %s') % self._remote_location)
        logger.debug("Checkout %s on %s" % (self._remote_location, self.location))
        self._process_files(self._remote_location, self.location)
        return int(time.time())

    def cleanup(self):
        pass
        
    def update(self):
        self._send_callback(self.callback_on_action_notify,_('Updating repository %s') % self._remote_location)
        self._process_files(self._remote_location, self.location)
        return int(time.time())

    def _process_files(self, src, tgt):
        for filename in os.listdir(src):
            sourcefile = os.path.join(src, filename)
            targetfile = os.path.join(tgt, filename)
            shutil.copy(sourcefile, targetfile)
            self._send_callback(self.callback_on_file_add,targetfile)
            
    def revert(self):
        pass

    def submit(self, auth, files, msg):
        logger.debug("Perform submit %s (%s) [%s]" % (self.location, files, msg))
        self._send_callback(self.callback_on_action_notify,_('Checking in'))
        return int(time.time())
