# -*- coding: utf-8 -*-
"""Copyright (c) 2014 Sergio Gabriel Teves
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

from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings
from openidmigration import get_user_token

import logging
logger = logging.getLogger('vertaal.openidmigration')

def home(request):
    return render_to_response("openidmig/message.html",
                              {'secondarysite': getattr(settings, 'ENABLE_MIG','')},
                              context_instance = RequestContext(request))    

@login_required
def token_generation(request):
    return render_to_response("openidmig/token.html",
                              {'tokenid': get_user_token(request.user),
                               'secondarysite': getattr(settings, 'ENABLE_MIG','')},
                              context_instance = RequestContext(request))    
