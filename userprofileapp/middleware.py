from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.conf import settings

class UserLocaleMiddleware(object):
    """
    looks for user language on profile
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                lang = request.user.get_profile().language    
            except:
                lang = translation.get_language_from_request(request)
            else:
                supported = dict(settings.LANGUAGES)
                if lang not in supported:
                    lang = translation.get_language_from_request(request)
            translation.activate(lang)
        request.LANGUAGE_CODE = translation.get_language()
    
    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
