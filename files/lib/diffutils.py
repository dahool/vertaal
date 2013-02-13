# -*- coding: utf-8 -*-
"""Copyright (c) 2013, Sergio Gabriel Teves
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

from common.cache.file import FileCache
from files.lib.diff_match_patch import diff_match_patch

import logging
logger = logging.getLogger('vertaal.files')

def create_diff_cache(submits):
    for s in submits:
        logger.debug("Processing diff for %s" % s.pofile.filename)
        make_file_diff(s.pofile, s)
        
def make_diff(a, b):
    dm = diff_match_patch()
    diffs = dm.diff_main(a,b)
    dm.diff_cleanupSemantic(diffs)
    out = []
    for (op, data) in diffs:
        text = (data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>"))
        if op == diff_match_patch.DIFF_INSERT:
            out.append("<ins class=\"diff_add\">%s</ins>" % text)
        elif op == diff_match_patch.DIFF_DELETE:
            out.append("<del class=\"diff_sub\">%s</del>" % text)
        elif op == diff_match_patch.DIFF_EQUAL:
            out.append("<span>%s</span>" % text)
    return "".join(out)
    
def make_diff_old(a, b):
    import difflib
    filename = hash(b.encode('utf-8')).hexdigest()
    fc = FileCache(filename, expireInMinutes = None, tempdir = settings.TEMP_UPLOAD_PATH, prefix = '')
    try:
        content = fc.load()
    except:
        logger.exception('load')
        content = None
    if not content:
        out = []
        s = difflib.SequenceMatcher(None, a, b)
        for e in s.get_opcodes():
            if e[0] == "replace":
                out.append('<del class="diff_chg">'+''.join(a[e[1]:e[2]]) + '</del><ins class="diff_add">'+''.join(b[e[3]:e[4]])+"</ins>")
            elif e[0] == "delete":
                out.append('<del class="diff_sub">'+ ''.join(a[e[1]:e[2]]) + "</del>")
            elif e[0] == "insert":
                out.append('<ins class="diff_add">'+''.join(b[e[3]:e[4]]) + "</ins>")
            elif e[0] == "equal":
                out.append(''.join(b[e[3]:e[4]]))
            else: 
                raise "Um, something's broken. I didn't expect a '" + `e[0]` + "'."
        content = ''.join(out)
        try:
            fc.save(content)
        except:
            logger.exception('save')
    return content

def make_file_diff(file_old, file_new, uniff=False):
    content_new = file_new.handler.get_content().decode('utf-8')
    content_old = file_old.handler.get_content().decode('utf-8')
    if uniff:
        return make_udiff(content_old, content_new)
    return make_diff(content_old, content_new)

def make_udiff(a, b):
    import urllib
    dm = diff_match_patch()
    diffs = dm.diff_main(a,b)
    patches = dm.patch_make(diffs)
    out = []
    for patch in patches:
        if patch.length1 == 0:
            coords1 = str(patch.start1) + ",0"
        elif patch.length1 == 1:
            coords1 = str(patch.start1 + 1)
        else:
            coords1 = str(patch.start1 + 1) + "," + str(patch.length1)
        if patch.length2 == 0:
            coords2 = str(patch.start2) + ",0"
        elif patch.length2 == 1:
            coords2 = str(patch.start2 + 1)
        else:
            coords2 = str(patch.start2 + 1) + "," + str(patch.length2)
        text = ["@@ -", coords1, " +", coords2, " @@\n"]
        # Escape the body of the patch with %xx notation.
        for (op, data) in patch.diffs:
            data = data.encode("utf-8")
            txt = urllib.quote(data, "\"!~*'();/?:@&=+$,# ")
            #txt = (data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>"))            
            if op == diff_match_patch.DIFF_INSERT:
                text.append("<ins class=\"diff_add\">+%s</ins>" % txt)
            elif op == diff_match_patch.DIFF_DELETE:
                text.append("<del class=\"diff_sub\">-%s</del>" % txt)
            elif op == diff_match_patch.DIFF_EQUAL:
                text.append("<span>%s</span>" % txt)
            # High ascii will raise UnicodeDecodeError.  Use Unicode instead.
        out.append("".join(text))
    return "".join(out)        