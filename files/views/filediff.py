# -*- coding: utf-8 -*-
"""Copyright (c) 2012, Sergio Gabriel Teves
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
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from files.models import POFile
from files.lib.diffutils import make_file_diff

@login_required
def view_file_diff(request, slug, uniff=False):
    pofile = get_object_or_404(POFile, slug=slug)
    redirect = HttpResponseRedirect(reverse('commit_queue'))
    
    if pofile.submits.all_pending():
        s = pofile.submits.get_pending()
        content = make_file_diff(pofile, s, uniff)
        return render_to_response("files/file_diff.html",
                                   {'body': content,
                                    'pofile': pofile},
                                   context_instance = RequestContext(request))
    else:
        return redirect

