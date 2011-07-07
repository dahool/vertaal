from django import template
from django.utils.encoding import force_unicode

register = template.Library()

@register.inclusion_tag('tags/error.html')
def error(field):
    if hasattr(field,'errors') and field.errors:
        message = u','.join([u'%s' % force_unicode(e) for e in field.errors])
    else:
        return {'message': None}
    return {'message': message}

@register.inclusion_tag('tags/formfield.html')
def formfield(field):
    return {'field': field}