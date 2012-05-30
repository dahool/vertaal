from __future__ import with_statement
import os
from django.conf import settings
from datetime import datetime as dt

from app.log import (logger)

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
            # 15 minutes
            diff = dt.now() - b.updated
            diffm = (diff.seconds/60)
            if b.is_locked or diff.seconds < 900:
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
                del man
        
    def get_content(self, update = False):
        if update:
            self.update_repo()
            
        filef = file(self.pofile.file, 'rU')
        file_content = filef.read()
        filef.close()
        return file_content

class POTFileHandler(POFileHandler):

    def get_content(self):
        path = unicode(self.pofile.file)
        filef = file(path, 'rU')
        file_content = filef.read()
        filef.close()
        return file_content
    
class SubmitFileHandler(POFileHandler):

    def get_content(self):
        # this is not really a pofile, but a POFileSubmit
        path = unicode(self.pofile.file)
        filef = file(path, 'rU')
        file_content = filef.read()
        filef.close()
        return file_content