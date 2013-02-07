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
import time
import datetime
import types
from decimal import *

from django.http import HttpResponse
from django.db import models
from django.utils import simplejson as json
from django.core.serializers.json import DateTimeAwareJSONEncoder

def isiterable(elem):
    import collections
    if hasattr(collections, "Iterable"):
        return isinstance(elem, getattr(collections, "Iterable"))
    else:
        try:
            iter(elem)
        except:
            return False
        else:
            return True
    
def XMLResponse(data):
    response = HttpResponse(mimetype='text/xml')
    xml = '<?xml version="1.0" encoding="UTF-8"?><response>'
    for k in data.iterkeys():
        if k[-5:]=='_HTML':
            key = k[:-5]
            xml += '<%(key)s><![CDATA[%(value)s]]></%(key)s>' % ({'key': key, 'value': data[k]})
        else:
            if isiterable(data[k]):
                for kvalue in data[k]:
                    xml += '<%(key)s>%(value)s</%(key)s>' % ({'key': k, 'value': kvalue})    
            else:
                xml += '<%(key)s>%(value)s</%(key)s>' % ({'key': k, 'value': data[k]})
    xml += '</response>'
    response.write(xml)
    return response

def JJONResponse(data):
    resp = []
    for k in data.iterkeys():
        resp.append('"%s": %s' % (k, parse(data[k])))
    data = '{%s}' % ','.join(resp)
    return HttpResponse(data, mimetype='application/json')    
    
def parse(data):
    """
    The main issues with django's default json serializer is that properties that
    had been added to a object dynamically are being ignored (and it also has 
    problems with some models).
    """

    def _any(data):
        ret = None
        if type(data) is types.ListType:
            ret = _list(data)
        elif type(data) is types.DictType:
            ret = _dict(data)
        elif isinstance(data, Decimal):
            # json.dumps() cant handle Decimal
            ret = float(data)
        elif isinstance(data, models.query.QuerySet):
            # Actually its the same as a list ...
            ret = _list(data)
        elif isinstance(data, models.Model):
            ret = _model(data)
        elif isinstance(data, datetime.date):
            ret = time.strftime("%Y/%m/%d",data.timetuple())
        else:
            ret = data
        return ret
    
    def _model(data):
        ret = {}
        # If we only have a model, we only want to encode the fields.
        for f in data._meta.fields:
            ret[f.attname] = _any(getattr(data, f.attname))
        # And additionally encode arbitrary properties that had been added.
        fields = dir(data.__class__) + ret.keys()
        add_ons = [k for k in dir(data) if k not in fields]
        for k in add_ons:
            ret[k] = _any(getattr(data, k))
        return ret
    
    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret
    
    def _dict(data):
        ret = {}
        for k,v in data.items():
            ret[k] = _any(v)
        return ret
    
    ret = _any(data)
    
    return json.dumps(ret, cls=DateTimeAwareJSONEncoder)
