from django.conf import settings
from django.utils.translation import ugettext as _
from django.template import RequestContext, loader, Context
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from common.middleware.exceptions import Http403
from common.simplexml import XMLResponse
from userprofileapp.models import *
from userprofileapp.forms import UserProfileForm
from app.log import logger

@login_required
def update_favorites(request, remove=False, idtype=False):
    if request.method != 'POST':
        raise Http403

    res = {}
    if remove:
        id = False
        try:
            if idtype:
                id = request.POST.get('id')
                f = Favorite.objects.get(id=id)
            else:
                path = request.POST.get('path')
                f = Favorite.objects.get(url=path)
                id = f.id
                title = ''
            f.delete()
        except Exception, e:
            logger.error(e)
        if id:
            res['id'] = id
    else:
        title = request.POST.get('title')
        path = request.POST.get('path')
        if title.count("|") > 0:
            title = title.split("|")[1]
        title = title.strip()
        try:
            f = request.user.user_favorites.create(url=path,
                                               name=title)
            id = f.id
            res['id'] = id
            res['title'] = title
            res['path'] = path            
        except Exception, e:
            logger.error(e)
            
    if not idtype:
        page = render_to_string('favs.html',
                                {'path': path},
                                context_instance = RequestContext(request))
        res['content_HTML'] = page
    return XMLResponse(res)

@login_required
def account_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            u = form.save()
            lang = u.get_profile().language
            if lang and request.LANGUAGE_CODE <> lang:
                from django.utils import translation
                translation.activate(lang)
            request.user.message_set.create(
                            message=_("Profile updated."))            
    else:
        form = UserProfileForm(instance=request.user)
    return render_to_response("registration/profile.html",
                              {'form': form},
                               context_instance = RequestContext(request))

@login_required
def set_startup(request, remove=False):
    if request.method != 'POST':
        raise Http403

    res = {}
    res['id'] = fav_id = request.POST.get('id')
    profile = request.user.get_profile()
    if remove:
        res['success'] = True
        if profile.startup:
            try:
                profile.startup = None
                profile.save()
            except:
                res['success'] = False
    else:
        try:
            fav = Favorite.objects.get(id=fav_id)
            profile.startup = fav
            profile.save()
            res['success'] = True
        except:
            res['success'] = False
    return XMLResponse(res)
        
@login_required
def startup_redirect(request):
    try:
        profile = request.user.get_profile()
    except:
        profile = UserProfile.objects.create(user=request.user)
        
    if profile.startup is None:
        return HttpResponseRedirect(getattr(settings, 'STARTUP_REDIRECT_URL', reverse('user_profile')))
    else:
        return HttpResponseRedirect(profile.startup.url)