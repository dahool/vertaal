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
import os
import commands
import re
from common.utils.commands import *

def msgmerge(new_file, source, destination=None):
    
    if not destination:
        destination = source
        
    if os.name == "posix":
        command = "msgmerge %(new)s %(source)s --previous -N -o %(dest)s " % {'new': new_file,
                                                                   'source': source,
                                                                   'dest': destination}
        output = get_command_output(command)
               
    else:
        import shutil
        try:
            shutil.copy(new_file, destination)
            output = ''
        except Exception, e:
            output = str(e)

    return output

def msgfmt_check(pofile, lang='C'):
    """
    Run a `msgfmt -c` on a file (file object).
    Raises a ValueError in case the file has errors.
    """
    error = False
    
    if lang!='C':
        lang += '.UTF8'
    
    dirn = os.path.dirname(pofile)
    os.chdir(dirn)
    
    if os.name == "posix":
        command = "LC_ALL=%(lang)s LANG=%(lang)s LANGUAGE=%(lang)s msgfmt -c" \
                " %(file)s" % {'lang': lang, 'file': pofile}
    else:
        command = "msgfmt -c " + pofile

    output = get_command_output(command)
    
    try:
        os.remove(os.path.join(dirn, 'messages.mo'))
    except:
        pass
    
    if len(output)>0:
        msg = "$$".join(output)
        raise Exception, msg.replace(pofile,"")
    
#    (error, output) = commands.getstatusoutput(command)
#    
#    if error:
#        raise Exception, output.replace(os.path.dirname(pofile)+"/","")
        
def get_file_stats(pofile):
    """ Calculate stats for a POT/PO file """

    if os.name == "posix":
        command = "LC_ALL=C LANG=C LANGUAGE=C msgfmt --statistics" \
                  " -o /dev/null %s" % pofile
    else:
        command = "msgfmt --statistics %s" % pofile

    dirn = os.path.dirname(pofile)
    os.chdir(dirn)        
              
    output = ",".join(get_command_output(command))

    try:
        os.remove(os.path.join(dirn, 'messages.mo'))
    except:
        pass
    
    r_tr = re.search(r"([0-9]+) translated", output)
    r_un = re.search(r"([0-9]+) untranslated", output)
    r_fz = re.search(r"([0-9]+) fuzzy", output)

    if r_tr: translated = r_tr.group(1)
    else: translated = 0
    if r_un: untranslated = r_un.group(1)
    else: untranslated = 0
    if r_fz: fuzzy = r_fz.group(1)
    else: fuzzy = 0

    return {'translated' : int(translated),
            'fuzzy' : int(fuzzy),
            'untranslated' : int(untranslated)} 