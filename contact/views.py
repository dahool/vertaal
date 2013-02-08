from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from contact.forms import ContactForm
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

if settings.CONTACT_USE_CAPTCHA:
    from recaptcha.client import captcha
    
def contact(request, username = None):
    captcha_error = ""
    captcha_valid = True
    use_captcha = settings.CONTACT_USE_CAPTCHA and not request.user.is_authenticated()

    if request.method == 'POST':
        user = User.objects.get(username=request.POST.get('username'))
        username = user.username
        form = ContactForm(request.POST)
        if use_captcha:        
            captcha_response = captcha.submit(request.POST.get("recaptcha_challenge_field", None),  
                                           request.POST.get("recaptcha_response_field", None),  
                                           settings.RECAPTCHA_PRIVATE_KEY,  
                                           request.META.get("REMOTE_ADDR", None))  
            captcha_valid = captcha_response.is_valid
        if not captcha_valid:  
            captcha_error = "&error=%s" % captcha_response.error_code 
        else:
            if form.is_valid():
                if request.user.is_authenticated():
                    if request.user.first_name:
                        usern = '%s (%s)' % (request.user.get_full_name(), request.user.username)
                    else:
                        usern = request.user.username
                else:
                    usern = _('Anonymous (%(ip_address)s)') % {'ip_address': request.META.get("REMOTE_ADDR", "")}
                    
                subject = form.cleaned_data['subject']
                message = _('%(user)s wrote:') % {'user': usern} + "\n\n" + form.cleaned_data['message']
                message += '\n\n--\n' + _('This message was sent through the %(app_name)s contact form.\n') % {'app_name': getattr(settings, 'PROJECT_NAME')}
                sender = form.cleaned_data['sender']
                try:
                    mail = EmailMessage(subject=subject, body=message, to=[user.email], headers={'Reply-To': sender})
                    mail.send()
                    #user.email_user(subject, message, sender)
                except Exception, e:
                    logger.error(e)
                return render_to_response("contact/message.html",
                                          {'message': _('Your message has been sent.')},
                                          context_instance = RequestContext(request))
    else:
        user = User.objects.get(username=username)
        form = ContactForm()
        if request.user.is_authenticated():
            form = ContactForm(initial={'sender':request.user.email})
            
    return render_to_response("contact/contact.html",
                              {'form': form,
                               'captcha_error': captcha_error,
                               'settings': settings,
                               'use_captcha': use_captcha,
                               'username': username},
                               context_instance = RequestContext(request))