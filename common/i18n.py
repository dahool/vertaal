from django.utils import translation
from django.conf import settings

def set_user_language(user):
    try:
        lang = user.profile.get().language
        if lang:
            language = translation.to_locale(lang)
            translation.activate(language)
        else:
            # if user has no language and current is not default, then set the default
            # this is to avoid using the last selected language
            if not translation.get_language() == settings.LANGUAGE_CODE:
                language = translation.to_locale(settings.LANGUAGE_CODE)
                translation.activate(language)
        return language
    except:
        # in case of fail do nothing
        pass
        
class UserLanguage(object):
    '''Helper class to active/deactive language in with context
    '''
    
    def __init__(self, user):
        self.user = user
        
    def __enter__(self):
        l = set_user_language(self.user)
        return l
    
    def __exit__(self, type, value, traceback):
        translation.deactivate()
        
    def __del__(self):
        translation.deactivate()
