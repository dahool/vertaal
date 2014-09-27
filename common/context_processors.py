from django.conf import settings

def media(request):
    context_extras = {}
    context_extras['JQUERY'] = settings.JQUERY
    context_extras['JQUERY_UI'] = settings.JQUERY_UI
    return context_extras