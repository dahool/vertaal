# -*- coding: utf-8 -*-
"""Copyright (c) 2013, Sergio Gabriel Teves
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
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib import messages

from components.models import Component
from releases.models import Release
from languages.models import Language
from teams.models import Team
from files.models import POFile, POFileLog

def get_file_list(request, component=None, release=None, language=None):
    q = POFile.objects.filter()
    res = {}
    res['cookjar'] = {}
    if release:
        r = res['release'] = get_object_or_404(Release, slug=release)
        if r.read_only or r.project.read_only:
            if request.user.is_authenticated():
                messages.warning(request, _('This component is read only.'))
        q = q.filter(release=res['release'])
    if component:
        c = res['component'] = get_object_or_404(Component, slug=component)
        q = q.filter(component=res['component'])
    else:
        cook = 'cmpfilter_%s' % r.slug
        if request.POST.has_key('cmpfilter'):
            if request.POST.get('cmpfilter'):
                q = q.filter(component__in=request.POST.getlist('cmpfilter'))
                res['cfilter'] = [ int(i) for i in request.POST.getlist('cmpfilter') ]
        else:
            if cook in request.COOKIES:
                cf = request.COOKIES.get(cook).split(',')
                q = q.filter(component__in=cf)
                res['cfilter'] = [ int(i) for i in cf ]
            else:
                co = r.project.components.all()[0]
                q = q.filter(component=co)
                res['cfilter'] = [int(co.pk)]
                
    if language:
        l = res['language'] = get_object_or_404(Language, code=language)
        q = q.filter(language=res['language'])
        if r:
            res['team'] = get_object_or_404(Team, language=l,project=r.project)

    if request.user.is_authenticated():
        cook = 'shide_%s' % r.slug
        if request.POST.has_key('hideTranslated'):
            if request.POST.get('hideTranslated')=='true':
                q = q.extra(where=['total>trans'])
                res['cookjar'][cook] = 'true'
                res['hideTranslated'] = 'true'
            else:
                res['cookjar'][cook] = None
        else:
            if cook in request.COOKIES:
                q = q.extra(where=['total>trans'])
                res['hideTranslated'] = 'true'
        
        cook = 'onlys_%s' % r.slug
        if request.POST.has_key('onlySelf'):
            if request.POST.get('onlySelf')=='true':
                q = q.filter(Q(assigns__translate__id=request.user.id) |
                             Q(assigns__review__id=request.user.id))
                res['cookjar'][cook] = 'true'
                res['onlySelf'] = 'true'
            else:
                res['cookjar'][cook] = None
        else:
            if cook in request.COOKIES:
                q = q.filter(Q(assigns__translate__id=request.user.id) |
                             Q(assigns__review__id=request.user.id))
                res['onlySelf'] = 'true'
                        
    res['file_list']=q
    res['last_actions'] = POFileLog.objects.last_actions(res['release'],10,res['language'])
    
    return res


