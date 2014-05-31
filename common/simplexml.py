from django.http import HttpResponse

def XMLResponse(data):
    response = HttpResponse(content_type = "text/xml; charset=utf-8")
    xml = '<?xml version="1.0" encoding="UTF-8"?><response>'
    for k in data.iterkeys():
        if k[-5:]=='_HTML':
            key = k[:-5]
            xml += '<%(key)s><![CDATA[%(value)s]]></%(key)s>' % ({'key': key, 'value': data[k]})
        else:    
            xml += '<%(key)s>%(value)s</%(key)s>' % ({'key': k, 'value': data[k]})
    xml += '</response>'
    response.write(xml)
    return response
    
    