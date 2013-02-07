from django.db import IntegrityError
from django.conf import settings
from django.core.mail import EmailMessage
from common.mail import send_mass_mail_em
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader, Context
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Permission, Group
from django.template.loader import render_to_string
from common.decorators import permission_required_with_403
from common.middleware.exceptions import Http403
from common.simplexml import XMLResponse
from projects.models import *
from languages.models import *
from files.models import POFile, POFileSubmit
from teams.models import *
from app.log import logger
from common.i18n import set_user_language
from django import forms
import thread
from django.utils.encoding import smart_unicode

from django.contrib import messages

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':4, 'cols':30}))
    
class SubmitTypeForm(forms.Form):
    type = forms.ChoiceField(SUBMISSION_TYPE, label=_('File submission'))
            
def team_detail(request, project, lang):
    logger.debug("Team detail %s - %s" % (project, lang))
    language = get_object_or_404(Language, code__iexact=lang)
    project = get_object_or_404(Project, slug=project)
    team = get_object_or_404(Team, project=project, language=language)
    if team.can_commit(request.user):
        files = POFileSubmit.objects.by_project_and_language(project, language)
    else:
        files = None
    return render_to_response("teams/team_detail.html",
        {'team': team,
         'submit_files': files}, 
          context_instance = RequestContext(request))
    
@login_required
def team_admin(request, id):
    logger.debug("Team admin %s" % (id))
    team = get_object_or_404(Team, pk=id)
    if not team.can_manage(request.user):
        raise Http403
    if request.method == 'POST':
        form = SubmitTypeForm(request.POST)
        if form.is_valid():
            team.submittype = form.cleaned_data['type']
            team.save()
            messages.success(request, _('Updated'))
    else:
        form = SubmitTypeForm(initial={'type': team.submittype})
    return render_to_response("teams/team_admin.html",
                              {'team': team,
                               'form': form},
                              context_instance = RequestContext(request))    

@login_required
def team_contact(request, id):
    logger.debug("Team contact %s" % (id))
    team = get_object_or_404(Team, pk=id)
    
    if not team.is_member(request.user) and not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        form = ContactForm(request.POST)
        userids = request.POST.getlist('contact_user')

        if form.is_valid():
            if request.user.first_name:
                usern = '%s (%s)' % (request.user.get_full_name(), request.user.username)
            else:
                usern = request.user.username
                
            subject = form.cleaned_data['subject']
            message = _('%(user)s wrote:') % {'user': usern} + "\n\n" + form.cleaned_data['message']
            message += '\n\n--\n' + _('This message was sent through the %(app_name)s contact form.\n') % {'app_name': getattr(settings, 'PROJECT_NAME')}
            
            userlist = User.objects.filter(username__in=userids)
            maillist = []
            for u in userlist:
                maillist.append(EmailMessage(subject=subject, body=message, to=[u.email], headers={'Reply-To': request.user.email}))

            try:
                send_mass_mail_em(maillist)
            except Exception, e:
                logger.error(e)
                messages.warning(request, _("Your message couldn't be delivered to one or more recipients."))
            else:                              
                messages.success(request, _('Your message has been sent.'))
        
            return HttpResponseRedirect(reverse('team_detail',
                                            kwargs={ 'project': team.project.slug,
                                                    'lang': team.language.code}))
    else:
        userids = []
        form = ContactForm()

    return render_to_response("teams/team_contact.html",
                              {'team': team,
                               'form': form,
                               'selected': userids},
                              context_instance = RequestContext(request))
        
@login_required
def team_create_update(request, slug=None):
    pass

@login_required
def team_delete(request, project, lang):
    logger.debug("Team delete %s - %s" % (project, lang))
    if request.method != 'POST':
        raise Http403

    p = Project.objects.get(slug=project)
    if not p.is_maintainer(request.user):
        return XMLResponse({'message': _('You are not authorized to perform this action')})
    
    l = get_object_or_404(Language, code=lang)
    res = {'success': True}
    try:
        t = Team.objects.get(language=l, project=p)
        t.delete()
        # start a thread to delete all files for this team
        thread.start_new_thread(_remove_team_files, (request, p, l))
    except Team.DoesNotExist:
        pass
    except Exception, e:
        raise
    return XMLResponse(res)

def _remove_team_files(request, project, language):
    logger.debug("Remove team files %s - %s" % (project, language))
    for pofile in POFile.objects.filter(language=language, release__project=project):
        logger.debug("Delete %s" % (smart_unicode(pofile)))
        pofile.delete()
    messages.info(request, _('Team %(lang)s [%(project)s] removed.') % {'lang': language.name, 'project': project.name})
    
@login_required
def join_accept(request, id, reject=False):
    logger.debug("Team petition management %s [%s]" % (id, str(reject)))
    joinreq = get_object_or_404(JoinRequest, id=id)
    team = joinreq.team
    
    if not team.can_manage(request.user):
        raise Http403

    set_user_language(joinreq.user)
    
    subject = getattr(settings,
                      'EMAIL_SUBJECT_PREFIX',
                      '') + _("Request to join the %(team)s team") % {'team': team.language.name}    

    if reject:
        message = render_to_string('teams/join_reject.mail', 
                                   {'team': team.language.name,
                                     'project': team.project.name})
    else:
        message = render_to_string('teams/join_accept.mail', 
                                   {'team': team.language.name,
                                     'project': team.project.name})
        team.members.add(joinreq.user)

    set_user_language(request.user)
    
    em = EmailMessage(subject=subject, body=message, to=[joinreq.user.email])
    try:
        em.send()
    except Exception, e:
        logger.error(e)
        
    joinreq.delete()
    
    return HttpResponseRedirect(reverse('team_admin',
                                        kwargs={ 'id': team.id,}))

@login_required
def join_request(request, teamid):
    logger.debug("Team join request %s" % (teamid))
    use_captcha = getattr(settings, 'JOIN_USE_CAPTCHA', True)

    if use_captcha:
        from recaptcha.client import captcha

    captcha_error = ""
    captcha_valid = True

    team = get_object_or_404(Team, id=teamid)
            
    back = HttpResponseRedirect(reverse('team_detail',
                                            kwargs={ 'project': team.project.slug,
                                            'lang': team.language.code}))

    if team.is_member(request.user):
        messages.warning(request, _('You are already a member of this team.'));
        return back
    elif request.user in [r.user for r in team.join_requests.all()]:
        messages.warning(request, _('You have already sent a join request.'));
        return back
        
    if request.method == 'POST':
        if use_captcha:        
            captcha_response = captcha.submit(request.POST.get("recaptcha_challenge_field", None),  
                                           request.POST.get("recaptcha_response_field", None),  
                                           settings.RECAPTCHA_PRIVATE_KEY,  
                                           request.META.get("REMOTE_ADDR", None))  
            captcha_valid = captcha_response.is_valid

        if not captcha_valid:
            captcha_error = "&error=%s" % captcha_response.error_code
        else:
            team.join_requests.create(user=request.user)
            
            if request.user.get_full_name():
                username = "%s (%s)" % (request.user.get_full_name(), request.user.username)
            else:
                username = request.user.username
            sendm = []
            sender = request.user.email
            for coord in team.coordinators.all():
                set_user_language(coord)
                subject = getattr(settings,
                              'EMAIL_SUBJECT_PREFIX',
                              '') + _("Request to join the team")
                message = render_to_string('teams/join.mail', 
                                   {'username': username,
                                         'team': team.language.name,
                                         'project': team.project.name,
                                         'teamid': teamid})
                sendm.append(EmailMessage(
                                          subject=subject,
                                          body=message,
                                          to=[coord.email],
                                          headers={'Reply-To': sender}))
            set_user_language(request.user)
            
            try:
                send_mass_mail_em(sendm)
            except Exception, e:
                logger.error(e)
            messages.success(request, _('Your request to join this team has been received.'));
            return HttpResponseRedirect(reverse('team_detail',
                                                kwargs={ 'project': team.project.slug,
                                                'lang': team.language.code}))
            
    return render_to_response("teams/join.html",
                              {'teamid': teamid,
                               'captcha_error': captcha_error,
                               'settings': settings,
                               'use_captcha': use_captcha,
                               'team': team},
                               context_instance = RequestContext(request))
        
@login_required
def add_member(request, teamid):
    logger.debug("Team add member %s - %s" % (teamid, request.POST.get('id')))
    if request.method != 'POST':
        raise Http403
    
    res = {}
    t = Team.objects.get(pk=teamid)
    if not t.can_manage(request.user):
        return XMLResponse({'message': _('You are not authorized to perform this action')})
    
    user = User.objects.get(username=request.POST.get('id'))
    
    if not user in t.coordinators.all():
        t.members.add(user)
    
    page = render_to_string('teams/team_admin_table.html',
                            {'team': t},
                            context_instance = RequestContext(request))    
    res['content_HTML'] = page
    return XMLResponse(res)

@login_required
def remove_member(request, teamid, userid):
    logger.debug("Team remove member %s - %s" % (teamid, userid))
    if request.method != 'POST':
        raise Http403
    
    res = {}
    t = Team.objects.get(pk=teamid)
    if not t.can_manage(request.user):
        return XMLResponse({'message': _('You are not authorized to perform this action')})

    user = User.objects.get(username=userid)
    t.remove_member(user)
    
    page = render_to_string('teams/team_admin_table.html',
                            {'team': t},
                            context_instance = RequestContext(request))    
    res['content_HTML'] = page
    return XMLResponse(res)

@login_required
def update_permission(request, teamid, userid, codename, remove = False):
    logger.debug("Team update permission %s - User %s - Codename %s - Remove %s" % (teamid, userid, codename, str(remove)))
    if request.method != 'POST':
        raise Http403

    res = {}
    t = Team.objects.get(pk=teamid)
    if not t.can_manage(request.user):
        return XMLResponse({'message': _('You are not authorized to perform this action')})
    
    user = User.objects.get(username=userid)
    if remove:
        user.user_permissions.remove(Permission.objects.get(codename=codename))
    else:
        user.user_permissions.add(Permission.objects.get(codename=codename))

    page = render_to_string('teams/team_admin_table.html',
                            {'team': t},
                            context_instance = RequestContext(request))    
    res['content_HTML'] = page
    return XMLResponse(res)
    
@login_required
def update_group(request, teamid, userid, group):
    logger.debug("Team update group %s - User %s - Group %s" % (teamid, userid, group))
#    if request.method != 'POST':
#        raise Http403
    
    res = {}
    team = Team.objects.get(pk=teamid)
    if not team.can_manage(request.user):
        return XMLResponse({'message': _('You are not authorized to perform this action')})

    user = User.objects.get(username=userid)
    if user in team.coordinators.all():
        if not team.project.is_maintainer(request.user):
            return XMLResponse({'message': _('You are not authorized to perform this action')})        
    
    if user in team.coordinators.all():
        team.coordinators.remove(user)
    elif user in team.committers.all():
        team.committers.remove(user)
    elif user in team.members.all():
        team.members.remove(user)
        
    if group == "member":
        team.members.add(user)
    elif group == "commit":
        team.committers.add(user)
    elif group == "coord":
        team.coordinators.add(user)
        try:
            user.groups.add(Group.objects.get(name='Coordinator'))
        except Exception, e:
            logger.error(e)
    
    page = render_to_string('teams/team_admin_table.html',
                            {'team': team},
                            context_instance = RequestContext(request))    
    res['content_HTML'] = page
    return XMLResponse(res)

@login_required
def add_team(request, project):
    logger.debug("Add team %s - %s" % (project, request.POST.get('code')))
    if request.method != 'POST':
        raise Http403

    p = Project.objects.get(slug=project)
    if not p.is_maintainer(request.user):
        return XMLResponse({'message': _('You are not authorized to perform this action')})
    
    code = request.POST.get('code')
    l = Language.objects.get(code=code)
    res = {}
    try:
        t = Team.objects.create(language=l, project=p)
        res['url'] = t.get_absolute_url()
        res['name'] = l.name
        res['code'] = l.code
    except Exception, e:
        raise
    return XMLResponse(res)