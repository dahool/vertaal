try:
    from app.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
    
from django.contrib.auth.backends import ModelBackend

class EmailAuthBackend(ModelBackend):
    """Allow users to log in with their email address"""
    def authenticate(self, email=None, password=None, **kwargs):
        # Some authenticators expect to authenticate by 'username'
        
        if email is None:
            email = kwargs.get('username')
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                user.backend = "%s.%s" % (self.__module__, self.__class__.__name__)
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return None