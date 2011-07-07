from time import time
from random import Random
from django.conf import settings

def generate_token(text):
    seed = time() * time() 
    ran = Random(seed)
    skey = getattr(settings, 'SECRET_KEY')
    salt = ''.join(ran.sample(skey, len(skey))) 
    try:
        import hashlib
    except ImportError:
        import sha
        return sha.new(salt + text).hexdigest()
    else:
        return hashlib.sha1(salt + text).hexdigest()
    pass