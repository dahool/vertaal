# -*- coding: utf-8 -*-
import os
import datetime

from django.db import models
#from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.encoding import smart_unicode
from django.template.defaultfilters import dictsort, dictsortreversed
from django.db.models import permalink
from django.core.files import storage
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.db.models import Q

from files.lib import msgfmt
from files.lib.filehandler import (POFileHandler, SubmitFileHandler, POTFileHandler)
import common.utils.slug as sluger
from components.models import Component
from languages.models import Language
from releases.models import Release
from django.conf import settings
from versioncontrol.models import BuildCache

from app.log import logger

from files.potutils import extract_creation_date

STATUS = {'UNREVIEWED': 0,
          'TRANSLATED': 1,
          'REVIEWED': 2,
          'COMPLETED': 3}

STATUS_CHOICES = (
    (0, _('Unreviewed')),
    (1, _('Translated')),
    (2, _('Reviewed')),
    (3, _('Completed')),
)

LOG_ACTION = {'ACT_LOCK_ADD': 'A',
        'ACT_LOCK_DEL': 'R',
        'ACT_UPLOAD': 'U',
        'ACT_SUBMIT': 'C',
        'ACT_REJECT': 'X',
        'ACT_UPDATE': 'M',
        'ACT_ADD': 'FA',
        'ACT_DEL': 'FR',
        'ST_TRAN': 'S1',
        'ST_REV': 'S2',
        'ST_COMPL': 'S3',
        'ST_UNREV': 'S0',
        'AS_TRA': 'AT',
        'AS_REV': 'AR',
        'RE_TRA': 'RT',
        'RE_REV': 'RR'}

LOG_ACTION_CHOICES =(
    (LOG_ACTION['ACT_LOCK_ADD'], _('Locked')),
    (LOG_ACTION['ACT_LOCK_DEL'], _('Unlocked')),
    (LOG_ACTION['ACT_UPLOAD'], _('Uploaded')),
    (LOG_ACTION['ACT_SUBMIT'], _('Submitted')),
    (LOG_ACTION['ACT_REJECT'], _('Rejected')),
    (LOG_ACTION['ACT_UPDATE'], _('Updated')),
    (LOG_ACTION['ACT_ADD'], _('Added')),
    (LOG_ACTION['ACT_DEL'], _('Removed')),
    (LOG_ACTION['ST_TRAN'], _('Translated')),
    (LOG_ACTION['ST_REV'], _('Reviewed')),
    (LOG_ACTION['ST_COMPL'], _('Completed')),
    (LOG_ACTION['ST_UNREV'], _('Need Review')),                     
    (LOG_ACTION['AS_TRA'], _('Assigned Translator')),
    (LOG_ACTION['AS_REV'], _('Assigned Reviewer')),    
    (LOG_ACTION['RE_TRA'], _('Removed Translator')),
    (LOG_ACTION['RE_REV'], _('Removed Reviewer')),    
)

class POFileManager(models.Manager):
    
    def by_language(self, language):
        """ Returns a list of objects statistics for a language."""
        q = self.filter(language=language)
        q.order_by('language')
        return q

    def all_updatable(self):
        q = self.filter(release__enabled=True,
                    release__read_only=False,
                    release__project__enabled=True,
                    release__project__read_only=False)
        q.order_by('language', 'component', 'release')
        return q
    
    def by_release_total(self, release):
        """
        Return a list of the total translation by languages for a release
        """
        from django.db import connection
        cursor = connection.cursor()

        cursor.execute("SELECT sum(t.trans), sum(t.fuzzy), "\
                       "sum(t.untrans), sum(t.total), t.language_id "\
                       "FROM pofile as t "\
                       "WHERE t.release_id=%s AND "\
                       "language_id is NOT NULL "\
                       "GROUP by language_id",
                       [release.id])
        postats = []

        for row in cursor.fetchall():
            l = Language.objects.get(id=row[4])
            po = self.model(trans=row[0],
                            fuzzy=row[1], 
                            untrans=row[2], 
                            total=row[3], 
                            filename=l.code, # Not used but needed
                            language=l)
            po.calculate_perc()
            postats.append(po)
        return dictsortreversed(postats,'trans_perc') 

    def component_by_release_total(self, component):
        """
        Return a list of the total translation by languages for a release
        """
        from django.db import connection
        cursor = connection.cursor()

        cursor.execute("SELECT sum(t.trans), sum(t.fuzzy), "\
                       "sum(t.untrans), sum(t.total), t.release_id "\
                       "FROM pofile as t "\
                       "WHERE t.component_id=%s AND "\
                       "language_id is NOT NULL "\
                       "GROUP by t.release_id",
                       [component.id])
        postats = []

        for row in cursor.fetchall():
            r = Release.objects.get(id=row[4])
            po = self.model(trans=row[0],
                            fuzzy=row[1], 
                            untrans=row[2], 
                            total=row[3],
                            release=r,
                            component=component,
                            filename="-")
            po.calculate_perc()
            postats.append(po)
        return postats
    
    def unmerged(self, languages, project, release=None):
        from django.db import connection
        cursor = connection.cursor()

        cache_lang = {}
        cache_rel = {}
        cache_comp = {}
        
        langq = ''
        for lang in languages:
            cache_lang[lang.id] = lang
            if len(langq) > 0: langq += ' OR '
            langq += str(lang.id)
            
        sql = "SELECT p.language_id,p.component_id, p.release_id, p.slug, p.total, p.filename, p.status, p.id "\
                "FROM pofile p INNER JOIN pofile_pot_pofiles pol ON pol.pofile_id = p.id "\
                "INNER JOIN pofile_pot pot ON pol.potfile_id = pot.id "\
                "INNER JOIN language l ON p.language_id = l.id "\
                "INNER JOIN components c ON p.component_id = c.id WHERE "
        if release:
            sql += "p.release_id = %s AND " % release.id
        if languages:
            sql += "(%s) AND " % langq
        sql += "c.project_id = %(project_id)s AND NOT (c.potlocation IS NULL OR c.potlocation = '') "\
                "AND pot.updated IS NOT NULL AND p.potupdated < pot.updated" % {'project_id': project.id}
        
        logger.debug(sql)
        logger.debug(cursor.execute(sql))
        
        list = []
        for row in cursor.fetchall():
            if release:
                r = release
            else:
                r = cache_rel.get(long(id=row[2]), Release.objects.get(id=row[2]))
                cache_rel[long(id=row[2])] = r
            l = cache_lang.get(long(row[0]), Language.objects.get(id=row[0]))
            cache_lang[long(row[0])] = l
            c = cache_comp.get(long(row[1]), Component.objects.get(id=row[1]))
            cache_comp[long(row[1])] = c
            po = self.model(slug=row[3]
                            ,total=row[4]
                            ,language=l
                            ,release=r
                            ,component=c
                            ,filename=row[5]
                            ,status=row[6]
                            ,id=row[7])
            list.append(po)
        return list
    
    def by_release_and_component_total(self, release, component):
        """
        Return a list of the total translation by languages for a release and component
        """
        from django.db import connection
        cursor = connection.cursor()

        cursor.execute("SELECT sum(t.trans), sum(t.fuzzy), "\
                       "sum(t.untrans), sum(t.total), t.language_id "\
                       "FROM pofile as t "\
                       "WHERE t.release_id=%s AND "\
                       "t.component_id=%s AND "\
                       "language_id is NOT NULL "\
                       "GROUP by language_id",
                       [release.id, component.id])
        postats = []

        for row in cursor.fetchall():
            l = Language.objects.get(id=row[4])
            po = self.model(trans=row[0],
                            fuzzy=row[1], 
                            untrans=row[2], 
                            total=row[3], 
                            filename=l.code, # Not used but needed
                            language=l)
            po.calculate_perc()
            postats.append(po)
        return dictsortreversed(postats,'trans_perc') 
        
class POFile(models.Model):
    """A POFile is a representation of a PO file structure.
    
    >>> from auditor import middleware
    >>> from projects.models import Project
    >>> u = User.objects.create(username="test",password="test")
    >>> middleware.LOGGED_USER = u    
    >>> p = Project.objects.create(name="Project Test")
    >>> r = Release.objects.create(name="Release Test", project=p)
    >>> c = Component.objects.create(name="Component Test", project=p)
    >>> l = Language.objects.create(code="es",name="Spanish")
    >>> f = POFile(filename="testfile.es.po", language=l, component=c, release=r)
    >>> f.set_stats(6,2,2)
    >>> f.save()
    >>> f = POFile.objects.get(slug='release-test-component-test-es-testfile-es-po')
    >>> f
    testfile.es.po (Component: Component Test - Release: Release Test)
    >>> f.slug
    u'release-test-component-test-es-testfile-es-po'
    >>> f.total
    10
    >>> f.trans_perc + f.fuzzy_perc + f.untrans_perc
    100
    >>> f.locked
    False
    >>> len(POFile.objects.by_language(l))
    1
    >>> POFile.objects.by_language(l)[0] == f
    True
    >>> POFile.objects.all_updatable()[0] == f
    True
    >>> f0 = POFile.objects.create(filename="testfile2.es.po", component=c, language=l, release=r)
    >>> f0.set_stats(2,2,2)
    >>> f0.save()
    >>> r2 = Release.objects.create(name="Release2 Test",project=p)
    >>> f0 = POFile.objects.create(filename="testfile2.es.po", component=c, language=l, release=r2)
    >>> f0.set_stats(2,2,2)
    >>> f0.save()
    >>> f1 = POFile.objects.by_release_total(r)[0]
    >>> f1.total
    Decimal("16")
    >>> f1.trans
    Decimal("8")
    >>> f2 = POFile.objects.component_by_release_total(c)[0]
    >>> f2.total
    Decimal("16")
    >>> f2.trans
    Decimal("8")
    >>> f2 = POFile.objects.component_by_release_total(c)[1]
    >>> f2.total
    Decimal("6")
    >>> f2.trans
    Decimal("2")
    >>> f3 = POFile.objects.by_release_and_component_total(r,c)[0]
    >>> f3.total
    Decimal("16")
    >>> f3.trans
    Decimal("8")
    """
        
#    content_type = models.ForeignKey(ContentType)
#    object_id = models.PositiveIntegerField()
#    object = generic.GenericForeignKey('content_type', 'object_id')
    
    slug = models.SlugField(max_length=255, editable=False, unique=True)
    
    total = models.PositiveIntegerField(default=0)
    trans = models.PositiveIntegerField(default=0)
    fuzzy = models.PositiveIntegerField(default=0)
    untrans = models.PositiveIntegerField(default=0)
    
    language = models.ForeignKey(Language)
    filename = models.CharField(null=False, max_length=255, db_index=True)

    file = models.CharField(max_length=500, default='')
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    # Normalized fields
#    trans_perc = models.FloatField(default=0)
#    fuzzy_perc = models.FloatField(default=0)
#    untrans_perc = models.FloatField(default=100)
    trans_perc = models.PositiveIntegerField(default=0)
    fuzzy_perc = models.PositiveIntegerField(default=0)
    untrans_perc = models.PositiveIntegerField(default=100)
    
    component = models.ForeignKey(Component, related_name="files")
    release = models.ForeignKey(Release, related_name="files")
    
    status = models.IntegerField(default=0, db_index=True, choices=STATUS_CHOICES)
    
    potupdated = models.DateTimeField(null=True, blank=True)
    
    # Managers
    objects = POFileManager()

    def __unicode__(self):
        return ugettext(u"%(file)s (Component: %(component)s - Release: %(release)s)") % {
            'file': self.filename,
            'component': self.component.name,
            'release': self.release.name,}

    def __repr__(self):
        return '<%(file)s (Component: %(component)s - Release: %(release)s)>' % {'file': self.filename,
                                                                                'component': self.component.name,
                                                                                'release': self.release.name,}

        
    class Meta:
        #unique_together = ("language", "component", "release", "filename")
        db_table  = 'pofile'
        ordering  = ('filename', 'language')
        get_latest_by = 'created'
        
    def save(self, *args, **kwargs):
        if self._get_pk_val() is None:
            self.set_slug()
        self.calculate_perc()
        super(POFile, self).save(*args, **kwargs)

    def set_slug(self):
        self.slug = "-".join([self.release.slug,self.component.slug,self.language.code,sluger._string_to_slug(self.filename)])

    def calculate_perc(self):
        """Update normalized percentage statistics fields."""
        try:
            self.trans_perc = round(self.trans * 100 / self.total,2)
            self.fuzzy_perc = round(self.fuzzy * 100 / self.total,2)
            self.untrans_perc = round(self.untrans * 100 / self.total,2)
        except Exception, e:
            self.trans_perc = 0
            self.fuzzy_perc = 0
            self.untrans_perc = 0

    def update_file_stats(self, save=True):
        stats = msgfmt.get_file_stats(self.file)
        self.set_stats(stats['translated'],stats['fuzzy'],stats['untranslated'])
        self.potupdated = extract_creation_date(self.file)
        if save:
            self.save()
    
    def set_stats(self, trans=0, fuzzy=0, untrans=0):
        self.total = trans + fuzzy + untrans
        self.trans = trans
        self.fuzzy = fuzzy
        self.untrans = untrans
        self.calculate_perc()
    
    @property
    def handler(self):
        return POFileHandler(self)
    
    @property
    def viewurl(self):
        if self.release.project.viewurl:
            if self.release.project.repo_type == 'svn':
                if self.release.vcsbranch == u'trunk':
                    branch = self.release.vcsbranch
                else:
                    branch = "branches/%s" % self.release.vcsbranch
            url = '%s/%s/%s/%s' % (self.release.project.viewurl,
                                    branch,
                                    self.component.get_path(self.language.code),
                                    self.filename)
            if self.release.project.viewurlparams:
                params = "&".join(self.release.project.viewurlparams.split(';'))
                url+="?" + params
            return url 
        else:
            return ''

    def guess_lang(self):
        """
        Try to find the language of the POFile.

        Return None if guess work fails.
        This method is currently specific for <lang>.po files.        
        """
        import os
        from os.path import basename
        try:
            lang_code = os.path.splitext(basename(self.filename[:-3:]))[1][1:]
            return Language.objects.get(code=lang_code)
        except:
            return

    @property
    def locked(self):
        if self.locks.all():
            return True
        else:
            return False

#    @property
#    def potfile(self):
#        try:
#            basename = os.path.splitext(os.path.splitext(self.filename)[0])[0]
#            return POTFile.objects.get(name='%s.pot' % basename,
#                                       release=self.release,
#                                       component=self.component)
#        except Exception, e:
#            return None
    
    @property
    def buildcachedata(self):
        b = BuildCache.objects.filter(component=self.component,
                                  release=self.release)
        if b.all():
            return b.get()
        else:
            return None
    
    @property
    def need_merge(self):
        if self.potfile.all():
            potfile = self.potfile.get()
#            if potfile.total != self.total and (potfile.updated is not None and potfile.updated > self.potupdated):
            if potfile.updated is not None and potfile.updated > self.potupdated:
                return True
        return False
                    
class POFileAssign(models.Model):
    pofile = models.ForeignKey(POFile, related_name='assigns', unique=True)
    translate = models.ForeignKey(User, null=True, blank=True, related_name="translator_of")
    review = models.ForeignKey(User, null=True, blank=True, related_name="reviewer_of")
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.pofile.filename
    
    def __repr__(self):
        return '<POFileAssign %s>' % self.pofile.filename
    
    class Meta:
        db_table = 'pofile_assigns'

class POTFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.CharField(max_length=500, default='')
    total = models.IntegerField(default=0)
    updated = models.DateTimeField(null=True, blank=True)
    release = models.ForeignKey(Release)
    component = models.ForeignKey(Component)
    pofiles = models.ManyToManyField(POFile, related_name='potfile')
    
    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<POTFile %s>' % self.name

    @property
    def handler(self):
        return POTFileHandler(self)

    def update_file_stats(self, save=True):
        stats = msgfmt.get_file_stats(self.file)
        self.total = stats['translated'] +  stats['fuzzy'] + stats['untranslated']
        self.updated = extract_creation_date(self.file)
        if save:
            self.save()
       
    class Meta:
        unique_together = ("component", "release", "name")
        db_table = 'pofile_pot'
        
class POTFileNotification(models.Model):
    pofile = models.ForeignKey(POFile)
    potfile = models.ForeignKey(POTFile)
    last = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return self.pofile.filename

    def __repr__(self):
        return '<POTFileNotification %s>' % self.pofile.filename
    
    class Meta:
        unique_together = ("pofile", "potfile")
        db_table = 'pofile_potnotification'
            
class POFileLock(models.Model):
    """A lock/hold on a POFile object.
    
    >>> f = POFile.objects.get(slug='release-test-component-test-es-testfile-es-po')
    >>> u = User.objects.get(username="test")
    >>> f0 = f.locks.create(owner=u)
    >>> f.locked
    True
    >>> f.locks.get()
    <POFileLock: testfile.es.po (test)>
    """
    
    pofile = models.ForeignKey(POFile, related_name='locks', null=True)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, related_name='files_locked') 
    
    class Meta:
        db_table = 'pofile_lock'
        unique_together = ('pofile', 'owner')
        ordering  = ('-created',)
        get_latest_by = 'created'
        
    def can_unlock(self, user):
        from teams.models import Team
        
        return (self.owner == user or
            Team.objects.get(project=self.pofile.release.project,
                             language=self.pofile.language).can_manage(user))
        
    def __unicode__(self):
        return u"%(pofile)s (%(owner)s)" % {
            'owner': self.owner.username,
            'pofile': self.pofile.filename,} 
    
    def __repr__(self):
        return '<Lock: %s>' % self.pofile.filename
    
class POFileLogManager(models.Manager):
    
    def last_actions(self, release, limit, language):
        from django.db import connection
        cursor = connection.cursor()
        
        try:
            bot = User.objects.get(username=getattr(settings, 'BOT_USERNAME','bot'))
        except:
            bot = None
        
        sql = "SELECT p.pofile_id, p.created, p.user_id, p.action, p.id "\
            "FROM pofile_log as p INNER JOIN pofile as f ON "\
            "p.pofile_id = f.id"
            
        sql += " WHERE f.release_id=%s" % release.id
        
        if language:
            sql += " AND f.language_id=%s" % language.id 
        if bot:
            sql += " AND p.user_id<>%s" % bot.pk
            
        sql += " ORDER BY id DESC LIMIT %s" % limit
               
        cursor.execute(sql)
              
        files = []
        for row in cursor.fetchall():
            pofile = POFile.objects.get(id=row[0])
            user = User.objects.get(id=row[2])
            po = self.model(id=row[4],
                            pofile=pofile,
                            user=user,
                            action=row[3],
                            created=row[1])
            files.append(po)
        return files        
        
    def distinct_actions(self, release, limit, language=None, user=None):
        from django.db import connection
        cursor = connection.cursor()

        sql = "SELECT p.pofile_id, p.created, p.user_id, p.action, p.id "\
            "FROM pofile_log as p INNER JOIN pofile as f ON "\
            "p.pofile_id = f.id"
            
        if user:
            sql += " LEFT OUTER JOIN pofile_assigns as a ON p.pofile_id = a.pofile_id"

        sql += " WHERE f.release_id=%s" % release.id
        
        if language:
            sql += " AND f.language_id=%s" % language.id 
        if user:
            sql += " AND (a.translate_id=%s or a.review_id=%s)" % (user.id,user.id)
            
        sql += " AND p.id = (SELECT max(id) FROM pofile_log m WHERE "\
            "m.pofile_id = p.pofile_id) LIMIT %s" % limit
               
        cursor.execute(sql)
              
        files = []
        for row in cursor.fetchall():
            pofile = POFile.objects.get(id=row[0])
            user = User.objects.get(id=row[2])
            po = self.model(id=row[4],
                            pofile=pofile,
                            user=user,
                            action=row[3],
                            created=row[1])
            files.append(po)
        return dictsortreversed(files, 'created')
    
    def latest_by_action(self):
        latest_by = self.model._meta.get_latest_by
        q = self.get_query_set()
        q.query.add_q(Q(action=LOG_ACTION['ACT_LOCK_DEL']))
        q.query.set_limits(high=1)
        q.query.add_ordering('-%s' % latest_by)
        return q
         
class POFileLog(models.Model):
    """A log record
    
    >>> f = POFile.objects.get(slug='release-test-component-test-es-testfile-es-po')
    >>> u = User.objects.get(username="test")
    >>> f.log.all()[0]
    <POFileLog: testfile.es.po :: Lock added by test>
    >>> f0 = f.log.create(user=u,action='R')
    >>> f1 = f.log.create(user=u,action='U')
    >>> POFileLog.objects.latest_by_action()[0]
    <POFileLog: testfile.es.po :: Lock removed by test>
    """
    
    pofile = models.ForeignKey(POFile, related_name='log')
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(User)
    action = models.CharField(max_length=2, db_index=True, choices=LOG_ACTION_CHOICES)
    comment = models.CharField(max_length=255, default='')
    
    objects = POFileLogManager()
    
    class Meta:
        db_table = 'pofile_log'
        ordering  = ('-created',)
        get_latest_by = 'created'

    def __unicode__(self):
        if self.action in ['M','FA','FR','S1','S2','S3','S0']:
            return _('%(pofile)s :: %(action)s') % {
                                        'pofile': self.pofile.filename,
                                        'action': self.get_action_display()}
        else:
            return _('%(pofile)s :: %(action)s by %(user)s') % {
                                        'pofile': self.pofile.filename,
                                        'action': self.get_action_display(),
                                        'user': self.user.username}
    
    def __repr__(self):
        return '<POFileLog: %s - Action: %s>' % (self.pofile.filename,
                                                 self.action)
    
class POFileSubmitManager(models.Manager):
    
    def by_project_and_language(self, project, language):
        files = self.filter(pofile__language=language,
                            pofile__release__project=project,
                            enabled=True).order_by('-created')
        return files

def get_upload_path(instance, filename):
    return instance.pofile.slug
   
class FileSystemStorage(storage.FileSystemStorage):
    """
    Subclass Django's standard FileSystemStorage to fix permissions
    of uploaded files.
    """
    def _save(self, name, content):
       name =  super(FileSystemStorage, self)._save(name, content)
       full_path = self.path(name)
       mode = getattr(settings, 'FILE_UPLOAD_PERMISSIONS', None)
       if not mode:
           mode = 0644
       os.chmod(full_path, mode)
       return name
   
class POFileSubmit(models.Model):
    """A file upload
    
    >>> f = POFile.objects.get(slug='release-test-component-test-es-testfile-es-po')
    >>> u = User.objects.get(username="test")
    >>> f0 = f.submits.create(owner=u,file='/tmp/filename')
    >>> str(f.submits.get())
    'testfile.es.po (test)'
    """
        
    pofile = models.ForeignKey(POFile, related_name='submits', null=True)
    created = models.DateTimeField(auto_now=True, auto_now_add=True, editable=True)
    owner = models.ForeignKey(User, related_name='files_submitted')
    enabled = models.BooleanField(default=True, db_index=True)
    locked = models.BooleanField(default=False, db_index=True)
    log_message = models.CharField(max_length=255, default='')
    file = models.FileField(max_length=500,
                            storage=FileSystemStorage(location=settings.UPLOAD_PATH),
                            upload_to=get_upload_path) 
    merge = models.BooleanField(default=True)
    objects = POFileSubmitManager()
    
    class Meta:
        db_table = 'pofile_submit'
        unique_together = ('pofile', 'owner')
        ordering  = ('-created',)
        get_latest_by = 'created'
    
    def __unicode__(self):
        return u"%(pofile)s (%(owner)s)" % {
            'owner': self.owner.username,
            'pofile': self.pofile.filename,} 

    def __repr__(self):
        return '<POFileSubmit: %s>' % self.pofile.filename
    
    def update(self, owner, file, log_message):
        self.owner = owner
        self.file = file
        self.log_message = log_message
        self.enabled = True
        self.locked = False
        
    @property
    def handler(self):
        return SubmitFileHandler(self)

def createlock_callback(sender, **kwargs):
    obj = kwargs['instance']
    try:
        POFileLog.objects.create(pofile=obj.pofile, user=obj.owner, action='A')
    except:
        pass    

def removelock_callback(sender, **kwargs):
    obj = kwargs['instance']
    try:
        POFileLog.objects.create(pofile=obj.pofile, user=obj.owner, action='R')
    except:
        pass
   
def addsubmit_callback(sender, **kwargs):
    obj = kwargs['instance']
    try:
        POFileLog.objects.create(pofile=obj.pofile, user=obj.owner, action='U')
    except:
        pass
    
def remove_pofile(sender, **kwargs):
    obj = kwargs['instance']
    if os.path.exists(obj.file):
        try:
            os.unlink(obj.file)
        except:
            pass
    
#post_delete.connect(unlock_callback, sender=POFileSubmit)
#post_delete.connect(removelock_callback, sender=POFileLock)
post_save.connect(createlock_callback, sender=POFileLock)
pre_delete.connect(remove_pofile, sender=POFile)
pre_delete.connect(remove_pofile, sender=POTFile)
#post_save.connect(addsubmit_callback, sender=POFileSubmit)

