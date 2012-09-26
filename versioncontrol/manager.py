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
from __future__ import with_statement
import os
import os.path
import glob
import shutil
import datetime
import re
import copy
import thread

from django.utils.translation import ugettext as _
from django.utils.encoding import smart_unicode
from django.core.mail import send_mass_mail
from django.template import loader, Context
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings

from files.models import POFile, POFileLog, POTFile, LOG_ACTION
from versioncontrol.lib.browser import BrowserAuth, RepositoryBrowserFactory, AuthException
from common.utils.lock import Lock, LockException
from common.i18n import set_user_language, UserLanguage
from files.lib import msgfmt
from versioncontrol.models import BuildCache
from auditor import middleware
from common.notification import FileUpdateNotification

from app.log import (logger)

from dateutil.parser import *

from files.potutils import extract_creation_date

class LockRepo(Lock):
    
    def __init__(self, project_slug, release_slug,
                        component_slug, lang_code):
        name = "_".join([project_slug, release_slug, component_slug, lang_code] )
        super(LockRepo, self).__init__(name=name)
    
class SubmitClient():
    
    def __init__(self, files, current_user, user, pword, message=''):
        self.files = files
        self.user = user
        self.pword = pword
        self.message = message
        self.current = current_user
        self.notifications = {}
        self.BOT_USER = User.objects.get(username=getattr(settings, 'BOT_USERNAME', 'bot'))
        self.notifier = FileUpdateNotification(self.BOT_USER, logger)
        
    def __add_notification(self, user, pofile):
        list = []
        if self.notifications.has_key(user.id):
            list = self.notifications.get(user.id)
        list.append(pofile)
        self.notifications[user.id] = list
    
    def __unlock_submits(self, smfiles):
        for smfile in smfiles:
            smfile.locked = False
            smfile.save()
            
    def __process_notifications(self):
        logger.debug("Init")
        mlist = []
        try:
            for id in self.notifications.keys():
                user = User.objects.get(pk=id)
                with UserLanguage(user) as user_lang:
                    subject = getattr(settings, 'EMAIL_SUBJECT_PREFIX','') + _("Files submitted")
                    message = render_to_string('updater/confirmcommit.mail', {'files': self.notifications.get(id)})
                    mlist.append((subject, message, None, [user.email]))
            send_mass_mail(mlist, True)
            set_user_language(self.current)
            self.notifier.process_notifications()
        except Exception, e:
            logger.error(str(e))
            logger.exception('__process_notifications')
        logger.debug("End")
        
    def run(self):
        """ it is supposed all the files in the list 
            are from the same project.
            So I will create a lock for the project to avoid conflicts
        """
        logger.debug("init")
        releases = {}
        exceps = []
        for smfile in self.files:
            c = {}
            f = []
            # lets lock the submitfile to avoid conflics
            smfile.locked = True
            smfile.save()
            pofile = smfile.pofile
            rkey = "_".join([pofile.release.project.slug,pofile.release.slug])
            ckey = pofile.component.slug
            if releases.has_key(rkey):
                c = releases.get(rkey)
            if c.has_key(ckey):
                f = c.get(ckey)
            f.append(smfile)
            c[ckey] = f
            releases[rkey] = c

        for key, release in releases.items():
            for component in release.itervalues():
                lang = component[0].pofile.language.code
                message = []
                if self.message:
                    message.append(self.message)
                try:
                    # lets update the POT first
                    if component[0].pofile.component.potlocation:
                        potup = POTUpdater(component[0].pofile.release.project,
                                           component[0].pofile.release,
                                           component[0].pofile.component)
                        potup.refresh()
                        del potup
                    with LockRepo(component[0].pofile.release.project.slug,
                             component[0].pofile.release.slug,
                             component[0].pofile.component.slug,
                             component[0].pofile.language.code) as lock:
                        v = Manager(component[0].pofile.release.project,
                                           component[0].pofile.release,
                                           component[0].pofile.component,
                                           component[0].pofile.language)
                        v.revert()
                        v.refresh()
                        commit_files = []
                        commit_files_notice = []
                        for smfile in component:
                            sfilename = smart_unicode(smfile.file)
                            if os.path.exists(sfilename):
                                if smfile.merge:
                                    if smfile.pofile.need_merge:
                                        try:
                                            pot = smfile.pofile.potfile.get()
                                            logger.debug("Merge file %s with %s." % (smfile.pofile.file, pot.file))
                                            # merge first the current file with the pot file
                                            out = msgfmt.msgmerge(smfile.pofile.file, pot.file)                                            
                                        except POTFile.DoesNotExist:
                                            out = 0
                                        if not len(out) > 1:
                                            logger.debug("Merge file %s with %s." % (sfilename, smfile.pofile.file))
                                            out = msgfmt.msgmerge(sfilename, smfile.pofile.file)
                                    else:
                                        logger.debug("Merge file %s with %s." % (sfilename, smfile.pofile.file))
                                        out = msgfmt.msgmerge(sfilename, smfile.pofile.file)
                                else:
                                    try:
                                        logger.debug("Copy file %s to  %s." % (sfilename, smfile.pofile.file))
                                        shutil.copy(sfilename, str(smfile.pofile.file))
                                        out = ''
                                    except Exception, e:
                                        out = str(e)
                                if len(out)>1:
                                    raise Exception(_('An error occurred while performing file merge. %s' % ";".join(out)))
                                # create a backup, just in case
                                if getattr(settings, 'BACKUP_UPLOADS', True):
                                    newname = '%s.%s.bak' % (sfilename, datetime.datetime.now().strftime('%Y%m%d%H%M'))
                                    logger.debug("Backup file %s" % newname)
                                    shutil.copy(sfilename, newname)
                                    os.chmod(newname, getattr(settings, 'FILE_UPLOAD_PERMISSIONS',0664))
                                
                                # files to be commited
                                commit_files.append(str(smfile.pofile.file))
                                # notification list
                                commit_files_notice.append((smfile.owner, smfile.pofile))
                                message.append('%s: %s (%s)' % (smfile.pofile.filename,smfile.log_message, smfile.owner.username))
                            else:
                                logger.error("File %s does not exists [%s]" % (sfilename,smfile.id))
                                raise Exception(_('The system was unable to find the file id %(id)s. Please open a support ticket [%(url)s]') % 
                                                {'id':smfile.id, 'url': getattr(settings, 'TICKET_URL','')})
                        message.append('\n\nCommitted with %s on behalf of %s' % (getattr(settings, 'PROJECT_NAME'),self.current))
                        commit_message = "\n".join(message)
                        rev = v.commit(self.user, self.pword, commit_files, commit_message)
                        
                        for fowner, fpo in commit_files_notice:
                            self.__add_notification(fowner, fpo)
                        
                        try:
                            bc = BuildCache.objects.get(component=component[0].pofile.component,
                                                        release=component[0].pofile.release)
                            bc.setrev(rev)
                            bc.save()
                        except BuildCache.DoesNotExist:
                            pass
                        except Exception, e:
                            logger.error(e)

                        if rev:
                            if self.message:
                                cmessage = _('%(message)s (Committed revision %(revision)s)') % {'message': self.message, 'revision': rev}
                            else:
                                cmessage = _('Committed revision %s') % rev
                        else:
                            logger.debug("Revision is: %s" % str(rev))
                            cmessage = self.message
                                                        
                        for smfile in component:
                            old_instance = copy.copy(smfile.pofile)
                            smfile.pofile.update_file_stats(True)
                            self.notifier.check_notification(smfile.pofile, old_instance, False)
                            try:
                                smfile.pofile.locks.get().delete()
                                POFileLog.objects.create(pofile=smfile.pofile, user=smfile.owner, action=LOG_ACTION['ACT_LOCK_DEL'], comment=smfile.log_message)
                            except:
                                pass
                            smfile.delete()
                            POFileLog.objects.create(pofile=smfile.pofile, user=self.current, action=LOG_ACTION['ACT_SUBMIT'], comment=cmessage)
                            try:
                                self.files.remove(smfile)
                            except:
                                pass
                            
                except LockException, e:
                    # unlock remaining files
#                    for f in self.files:
#                        f.lock = False
#                        f.save()
                    self.__unlock_submits(component)
                    logger.error(e)
                    #raise Exception(_('The project is locked. Please try again in a few minutes'))
                    exceps.append(_('Component %(component)s is locked for language %(lang)s. Please try again in a few minutes') % 
                                  {'component': component[0].pofile.component.name, 'lang': component[0].pofile.language.name})
                except Exception, e:
                    logger.error(e)
                    if str(e).count('callback_get_login')>0:
                        self.__unlock_submits(self.files)
                        logger.error("Fail login")
                        raise AuthException(_('Authentication error. Check your username and password.'))
                    elif str(e).count('callback_ssl_server_trust_prompt')>0:
                        self.__unlock_submits(self.files)
                        logger.error("Fail trust SSL")
                        raise AuthException(_('SSL Validation error. If the problem persist contact the repository administrator.'))
                    else:
                        self.__unlock_submits(component)
                        exceps.append(str(e))
                
        thread.start_new_thread(self.__process_notifications, ())
        set_user_language(self.user)

        if len(exceps)>0:
            raise Exception("\n".join(exceps))
        
        logger.debug("end")

def get_repository_location(project, release, component, lang):
    return os.path.join(getattr(settings,'REPOSITORY_LOCATION'), get_repository_path(project, release, component, lang))

def get_repository_path(project, release, component, lang):
    return os.path.join(project.slug, release.slug, component.slug, lang.code)

def get_potrepository_path(project, release, component):
    return os.path.join(project.slug, release.slug, component.slug, 'POT-CACHE')

def normalize_path(basepath, filepath):
    bp = basepath.replace('\\','/')
    fp = filepath.replace('\\','/')
    return fp[fp.find(bp):]
    
class Manager(object):
    
    def __init__(self, project, release, component, lang, log = None, user=None):
        self.post_process = []
        
        self._init_location(project, release, component, lang)
        
        self.user = user
        self._create_log(log)
        
        self.project = project
        self.component = component
        self.release = release
        self.language = lang

        browserObj = RepositoryBrowserFactory.get_browser(project.repo_type) 
        self.browser = browserObj(self.location, 
                                  project.vcsurl,
                                  self.path, release.vcsbranch)

        self.browser.callback_on_action_notify =  self.notify_callback
        self.browser.callback_on_file_delete = self.__on_file_delete
        self.browser.callback_on_file_add = self.__on_file_add
        self.browser.callback_on_file_update = self.__on_file_add
        
        if project.repo_user and project.repo_pwd:
            self.browser.auth = BrowserAuth(project.repo_user, project.get_repo_pwd())
        
    def _init_location(self, project, release, component, lang):
        self.path = component.get_path(lang.code)
        self.basepath = get_repository_path(project, release, component, lang)
        self.location = get_repository_location(project, release, component, lang)

        if not os.path.exists(self.location):
            os.makedirs(self.location, 0777)
        
    def _create_log(self, log):
        if log:
            if hasattr(log, 'writelines'):
                self.log = log
            else:
                self.log = open(log,'a+')
        else:
            self.log = None
            
    def __del__(self):
        if self.log:
            self.log.close()

    def __on_action(self, sender, **kw):
        logger.debug(kw['arg_dict'])
        
    def notify_callback(self, message):
        logger.debug(message)
        if self.log:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log.writelines('[%s] - %s\n' % (now,message))
            self.log.flush()

    def build(self):
        logger.debug("init")
        rev = self.browser.init_repo()
        self._do_post_process()
        self.update_stats(False)
        logger.debug("end")
        return rev
        
    def revert(self):
        logger.debug("revert")
        self.browser.revert()

    def refresh(self):
        logger.debug("init")
        rev = self.browser.update()
        self._do_post_process()
        logger.debug("end")
        return rev
        
    def _do_post_process(self):
        '''files are not created on event raise. so we need to check it at the end
        '''
        logger.debug("do post process")
        for pf in self.post_process:
            self.notify_callback(_('Processing %s') % pf.filename)
            self.__fill_extrafile_data(pf)
            pf.save()
        logger.debug("end post process")
                    
    def __fill_extrafile_data(self, file):
        logger.debug("Extract date %s" % file.filename)
        file.potupdated = extract_creation_date(file.file)
        
    def __on_file_delete(self, path):
        if path.endswith('.po'):
            logger.debug("Process delete %s" % path)
            try:
                file = POFile.objects.get(filename=os.path.basename(path),
                                          component=self.component,
                                          release=self.release,
                                          language=self.language)
                logger.debug("Delete %s" % path)
                file.delete()
            except POFile.DoesNotExist:
                logger.debug("Nothing to do")
                pass
            except Exception, e:
                logger.error(e.args)
                raise
    
    def __on_file_add(self, path):
        if path.endswith('.po'):
            logger.debug("Process add %s" % path)
            try:
                file = POFile.objects.get(filename=os.path.basename(path),
                                          component=self.component,
                                          release=self.release,
                                          language=self.language)
                # just in case we decided to change the path :)
                logger.debug("Update %s" % path)
                if not file.file == path:
                    file.file = path
                    self.post_process.append(file)
                    # the file doesn't exists yet
                    #file.potupdated = extract_creation_date(path)
                    file.save()
                #file.update_file_stats(True)
            except POFile.DoesNotExist:
                logger.debug("Add %s" % path)
                #potupdated = extract_creation_date(path)    
                file = POFile.objects.create(filename=os.path.basename(path),
                                          component=self.component,
                                          release=self.release,
                                          language=self.language,
                                          file=path)
                self.post_process.append(file)           
                if self.user:
                    try:
                        file.log.create(user=self.user, action='FA')
                    except Exception, e1:
                        logger.error(e1)
            except Exception, e:
                logger.error(e)
                raise
        
    def update_stats(self, update=True):
        logger.debug("init")

        if update:
            self.refresh()

        pofiles = POFile.objects.filter(component=self.component,
                                      release=self.release,
                                      language=self.language)
        for pofile in pofiles:
            try:
                self.notify_callback(_('Update statistics for %s') % pofile.filename)
                pofile.update_file_stats(True)
            except Exception, e:
                logger.error(e)
 
        self.notify_callback(_('Language %s complete.') % self.language.name)
        logger.debug("end")
        
    def commit(self, user, password, files, message):
        logger.debug("init")
        try:
            rev = self.browser.submit(BrowserAuth(user, password), files, message)
        except:
            logger.debug("Error while commiting. Trying revert.")
            self.browser.cleanup()
            self.browser.revert()
            raise
        
        logger.debug("end")
        return rev
    
class POTUpdater(Manager):
    
    def __init__(self, project, release, component, lang=None, log=None, user=None):
        super(POTUpdater, self).__init__(project, release, component, lang, log, user)
        self.notify_callback(_('Starting POT processing'))
                
    def _init_location(self, project, release, component, lang):
        self.path = '%s/%s' % (component.vcspath, component.potlocation)
        self.basepath = get_potrepository_path(project, release, component)
        self.location = os.path.join(getattr(settings,'REPOSITORY_LOCATION'), self.basepath)

        if not os.path.exists(self.location):
            os.makedirs(self.location, 0777)
        
    def update_stats(self, update=True):
        logger.debug("init")

        if update:
            self.refresh()

        potfiles = POTFile.objects.filter(component=self.component,
                                      release=self.release)
        for potfile in potfiles:
            try:
                self.notify_callback(_('Update statistics for %s') % potfile.name)
                potfile.update_file_stats()
            except Exception, e:
                logger.error(e)
 
        self.notify_callback(_('Completed.'))
        logger.debug("end")
    
    def __on_file_delete(self, path):
        if path.endswith('.pot'):
            logger.debug("Process delete %s" % path)
            try:
                filename = os.path.basename(path)
                file = POTFile.objects.get(name=filename,
                                           component=self.component,
                                           release=self.release)
                logger.debug("Delete %s" % path)
                file.delete()
            except POTFile.DoesNotExist:
                logger.debug("Nothing to do")
                pass
            except Exception, e:
                logger.error(e.args)
                raise
    
    def add_pofiles(self, potfile):
        basename = os.path.splitext(potfile.name)[0] + "."
        inpo = [pofile.pk for pofile in potfile.pofiles.all()]
        pofiles = POFile.objects.filter(filename__startswith=basename,
                              component=self.component,
                              release=self.release).exclude(pk__in=inpo)

        for pofile in pofiles:
            potfile.pofiles.add(pofile)
            
    def __on_file_add(self, path):
        if path.endswith('.pot'):
            logger.debug("Process %s" % path)
            try:
                filename = os.path.basename(path)
                file = POTFile.objects.get(name=filename,
                                           component=self.component,
                                           release=self.release)
                # just in case we decided to change the path :)
                logger.debug("Update %s" % path)
                if not file.file == path:
                    file.file = path
                    file.save()
                self.add_pofiles(file)
                self.post_process.append(file)
            except POTFile.DoesNotExist:
                logger.debug("Add %s" % path)
                file = POTFile.objects.create(name=filename,
                              component=self.component,
                              release=self.release,
                              file=path)
                self.add_pofiles(file)                
                self.post_process.append(file)
            except Exception, e:
                logger.error(e)
                raise
