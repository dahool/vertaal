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
from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_init
from files.models import *
from timezones.fields import TimeZoneField

import logging
logger = logging.getLogger('vertaal.userprofile')

class UserAuditLog(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    ip = models.CharField(max_length=15)
    username = models.CharField(max_length=30)
    action = models.CharField(max_length=30)
    
    class Meta:
        ordering  = ('-created',)
    
class FavoriteManager(models.Manager):
    
    def by_path(self, url):
        return self.filter(url=url)
        
class Favorite(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=255, default='')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, related_name="user_favorites")
        
    objects = FavoriteManager()
    
    def __unicode__(self):
        return self.url

    def __repr__(self):
        return u'<Favorite: %s>' % self.url

    class Meta:
        unique_together = ("url","user")
        db_table  = 'user_favorites'
        
class UserFile(models.Model):
    pofile = models.ForeignKey(POFile)
    last_update = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(User, related_name="user_files")
    
    def __unicode__(self):
        return self.pofile.filename

    def __repr__(self):
        return u'<UserFile: %s>' % self.pofile.filename
    
    class Meta:
        unique_together = ("pofile","user")
        db_table  = 'user_files'
        ordering  = ('-last_update',)

class UserProfileManager(models.Manager):
    
    def get(self, *args, **kwargs):
        """ catch exception when userprofile doesn't exists and create a new one
        this is better than doing it every time I need the profile
        """
        if args:
            kwargs['user__id__exact'] = args[0] 
        print ">>>>>>>>>>>>>>> ESTOY USANDO EL MANAGER"
        return self.get_or_create(kwargs)
    
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    timezone = TimeZoneField(default='UTC')
    language = models.CharField(max_length=5, null=True, blank=True) 
    startup = models.ForeignKey(Favorite, null=True, blank=True)
    
    objects = UserProfileManager()
    _default_manager = UserProfileManager()
    
    def __unicode__(self):
        return self.user.username

    def __repr__(self):
        return u'<Profile: %s>' % self.user.username
    
    class Meta:
        db_table  = 'user_profile'    

def add_user_file(sender, **kwargs):
    obj = kwargs['instance']
    logger.debug("Enter: %s" % obj.pofile)
    try:
        uf = UserFile.objects.get(pofile=obj.pofile, user=obj.owner)
        uf.save()
        logger.debug("Already exists. Updated")
    except:
        logger.debug("Adding file")
        try:
            uf = UserFile.objects.create(pofile=obj.pofile, user=obj.owner)
        except Exception, e:
            logger.error(e)

def create_default_profile(sender, **kwargs):
    obj = kwargs['instance']
    if not hasattr(obj, '_profile_cache'):
        if obj.id:
            obj._profile_cache, created = UserProfile.objects.get_or_create(user=obj)

post_save.connect(add_user_file, sender=POFileLock)
post_save.connect(create_default_profile, sender=User)
post_init.connect(create_default_profile, sender=User)