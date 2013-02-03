from django import template
from django.utils.encoding import force_unicode

register = template.Library()

@register.inclusion_tag('tags/error.html')
def error(field):
    if not field.errors:
        return {'message': None}
    message = u','.join([u'%s' % force_unicode(e) for e in field.errors])
    return {'message': message}

@register.filter
def errormsg(field):
    try:
        if not field.errors:
            return ''
    except:
        return ''
    message = u','.join([u'%s' % force_unicode(e) for e in field.errors])
    return message