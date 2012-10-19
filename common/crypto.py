"""Copyright (c) 2009,2012 Sergio Gabriel Teves
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

from django.conf import settings
from blowfishcipher import cipher

class BCipher:
    
    def __init__(self, key=None):
        if not key:
            key = getattr(settings, 'CIPHER_KEY', settings.SECRET_KEY)
        self.__cipher = cipher(key)
        
    def encrypt(self, text):
        return self.__cipher.encrypt(text)
    
    def decrypt(self, b64text):
        return self.__cipher.decrypt(b64text)
        
if __name__ == '__main__':
    import sys
    print "INIT TEST"
    key = 'abcdefgh'
    text = "este es un TEXTO que hay que encriptar"
    print "ENCRYPT: %s" % text
    bc = BCipher(key)
    crypt = bc.encrypt(text)
    print "RESULT: %s" % crypt
    res = bc.decrypt(crypt)
    print "DESCRYPTED: %s" % res
    if len(sys.argv) > 1:
        print "DECRYPTING INPUT: %s" % sys.argv[1]
        res = bc.decrypt(sys.argv[1])
        print "PLAIN TEXT: %s" % res
    if res == text:
        print "Success"
    else:
        print "Fail"
