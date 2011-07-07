from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from common.view.decorators import render
from languages.models import Language
from projects.models import Project
from glossary.models import Glossary
from glossary.forms import GlossaryForm
from django.conf import settings

from glossary.lib import tbx

lang_session_key = 'glossary_lang'
project_session_key = 'glossary_project'

@render('glossary/glossary_form.html')
def create_update(request, project=None, lang=None, word_id=None):
    term = None
    
    if word_id is None:
        try:
            l = Language.objects.get(code=lang)
            p = Project.objects.get(slug=project, enabled=True)
        except:
            return HttpResponseRedirect(reverse('gloss_lang_selection'))
    else:
        term = get_object_or_404(Glossary, id=word_id)
        l = term.language
        p = term.project
    
    if request.method == 'POST':
        if term:
            form = GlossaryForm(request.POST, instance=term)
            message = _("Successfully updated translation for '%s'")
        else:
            form = GlossaryForm(request.POST)
            message = _("Successfully added translation for '%s'")

        if form.is_valid():
            try:
                t = form.save(p,l)
            except IntegrityError:
                request.user.message_set.create(message=_("'%s' already exists") % form.cleaned_data['word'])
                return {'lang': l,
                        'project': p,
                        'id': word_id,
                        'form': form}
            if term:
                t.history.create(user=request.user, translation=t.translation, action_flag='C')
            else:
                t.history.create(user=request.user, translation=t.translation, action_flag='A')
            request.user.message_set.create(message=message % t.word)
            return HttpResponseRedirect(reverse('gloss_list',
                                                kwargs={'project': p.slug,
                                                        'lang': l.code}))
    else:
        if term:
            form = GlossaryForm(instance=term)
        else:
            form = GlossaryForm()

    return {'lang': l,
            'project': p,
            'id': word_id,
            'form': form}

def remove_word(request, word_id=None):
    term = get_object_or_404(Glossary, id=word_id)
    term.delete()
    request.user.message_set.create(message=_("Removed translation for '%s'") % term.word)
    return HttpResponseRedirect(reverse('gloss_list',
                                        kwargs={'project': term.project.slug,
                                                'lang': term.language.code}))

@render('glossary/glossary_log.html')
@login_required
def show_log(request, word_id):
    term = get_object_or_404(Glossary, id=word_id)
    return {'term': term}
    
@render('glossary/language_selection.html')
def language_selection(request):
    return {'projects': Project.objects.filter(enabled=True).order_by('name'),
            'languages': Language.objects.all()}
    
@render('glossary/glossary_index.html')
def show_all(request, project = None, lang = None):
    red = False
    if lang is None:
        red = True
        if lang_session_key in request.COOKIES:
            lang = request.COOKIES.get(lang_session_key)
        else:
            lang = request.LANGUAGE_CODE

    if project is None:
        red = True
        if project_session_key in request.COOKIES:
            project = request.COOKIES.get(project_session_key)
        else:
            return HttpResponseRedirect(reverse('gloss_lang_selection'))    
    
    if red:
        response = HttpResponseRedirect(reverse('gloss_list',
                                            kwargs={'project': project,
                                                    'lang': lang}))
        return response
    else:
        try:
            l = Language.objects.get(code=lang)
            p = Project.objects.get(slug=project, enabled=True)
        except:
            return HttpResponseRedirect(reverse('gloss_lang_selection'))
        
    list = Glossary.objects.filter(language=l, project=p)

    cookjar = {lang_session_key: lang, project_session_key: project}
    
    return {'lang': l,
            'project': p,
            'list': list,
            'languages': Language.objects.all(),
            'projects': Project.objects.filter(enabled=True),
            'cookjar': cookjar}

def export_tbx(request, project, lang):
    
    try:
        l = Language.objects.get(code=lang)
        p = Project.objects.get(slug=project, enabled=True)
    except:
        return HttpResponseRedirect(reverse('gloss_lang_selection'))    

    list = Glossary.objects.filter(language=l, project=p)
    exfile = tbx.VertaalTbxFile()
    exfile.parse_glossary(list)

    response = HttpResponse(str(exfile), mimetype='application/xml; charset=UTF-8')
    response['Content-Disposition'] = '%s filename=%s' % ("attachment;", "%s_%s.tbx" % (p.slug,l.code))        
    return response