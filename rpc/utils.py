# -*- coding: utf-8 -*-
"""Copyright (c) 2012 Sergio Gabriel Teves
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