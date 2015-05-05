# -*- coding: utf-8 -*-
"""Copyright (c) 2012 Sergio Gabriel Teves
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from __future__ import with_statement
import os
from django.conf import settings
from datetime import datetime as dt
from django.utils.encoding import smart_unicode

import logging
logger = logging.getLogger('vertaal.files')

class POFileHandler():
    
    def __init__(self, pofile):
        self.pofile = pofile
    
    def update_repo(self):
        from versioncontrol.manager import Manager, LockRepo
        from versioncontrol.models import BuildCache
        
        do_update = True
        try:
            b = BuildCache.objects.get(component=self.pofile.component,
                                       release=self.pofile.release)
        except:
            b = BuildCache.objects.create(component=self.pofile.component,
                                          release=self.pofile.release)
        else:
            updategap = getattr(settings,'FILE_UPDATE_GAP',900)
            diff = dt.now() - b.updated
            diffm = (diff.seconds/60)
            if b.is_locked or updategap == 0 or diff.seconds < updategap:
                logger.debug("No need to update. Last updated %s. %s minutes ago. Current lock %s." % (
                                                                            b.updated,
                                                                            diffm,
                                                                            b.is_locked))
                do_update = False
            else:
                logger.debug("Updating. Last updated %s. %s minutes ago." % (b.updated,
                                                                             diffm))
                b.lock()

        if do_update:
            try:
                man = Manager(self.pofile.release.project,
                                   self.pofile.release,
                                   self.pofile.component,
                                   self.pofile.language)            
                with LockRepo(self.pofile.release.project.slug,
                              self.pofile.release.slug,
                              self.pofile.component.slug,
                              self.pofile.language.code) as lock:        
                    man.refresh()
            except Exception, e:
                logger.error(e)
                raise
            finally:
                b.unlock()
        
    def get_file_path(self):
        return smart_unicode(self.pofile.file)
        
    def get_content(self, update = False):
        if update:
            self.update_repo()
        with open(self.get_file_path(), 'rU') as filef:
            file_content = filef.read()
        #filef = file(self.get_file_path(), 'rU')
        #file_content = filef.read()
        #filef.close()
        return file_content

class POTFileHandler(POFileHandler):

    def get_content(self):
        filef = file(self.get_file_path(), 'rU')
        file_content = filef.read()
        filef.close()
        return file_content
    
class SubmitFileHandler(POFileHandler):

    def get_content(self):
        # this is not really a pofile, but a POFileSubmit
        filef = file(self.get_file_path(), 'rU')
        file_content = filef.read()
        filef.close()
        return file_content
