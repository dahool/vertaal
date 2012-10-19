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

from random import randrange
import base64
from blowfish import Blowfish
from django.conf import settings

class BCipher:
    
    def __init__(self, key=None):
        if not key:
            key = getattr(settings, 'CIPHER_KEY', settings.SECRET_KEY)
        if len(key) < 8: raise Exception('Key length must be greater than 8')
        self.__cipher = Blowfish(key)
        
    def encrypt(self, text):
        padtext = self.__pad_text(text)
        res = []
        for n in range(0,len(padtext),8):
            part = padtext[n:n+8]
            res.append(self.__cipher.encrypt(part))
        ciphertext = ''.join(res)
        return base64.b64encode(ciphertext)
    
    def decrypt(self, b64text):
        enctext = b64text
        try:
            ciphertext = base64.b64decode(enctext)
        except TypeError:
            # text is not encrypted
            return enctext
        res = []
        for n in range(0,len(ciphertext),8):
            part = ciphertext[n:n+8]
            res.append(self.__cipher.decrypt(part))
        cleartext = ''.join(res)
        return self.__depad_text(cleartext)

    # Blowfish cipher needs 8 byte blocks to work with
    def __pad_text(self, text):
        pad_bytes = 8 - (len(text) % 8)
        # try to deal with unicode strings
        asc_text = str(text)
        for i in range(pad_bytes - 1):
            asc_text += chr(randrange(0, 256))
        # final padding byte; % by 8 to get the number of padding bytes
        bflag = randrange(6, 248); bflag -= bflag % 8 - pad_bytes
        asc_text += chr(bflag)
        return asc_text

    def __depad_text(self, text):
        pad_bytes = ord(text[-1]) % 8
        if not pad_bytes: pad_bytes = 8
        return text[:-pad_bytes]
        
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
