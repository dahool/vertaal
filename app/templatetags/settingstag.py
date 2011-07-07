from django import template
from django.conf import settings
from django.template import Node, Template, Context, NodeList, VariableDoesNotExist, resolve_variable, TemplateSyntaxError

register = template.Library()

@register.simple_tag
def setting(name):
    return getattr(settings, name, '')

@register.tag(name='ifsetting')
def ifsetting(parser, token):
    
    try:
        tag, arg = token.split_contents()
    except:
        raise TemplateSyntaxError, "%r takes 1 argument" % token.split_contents()[0]
    end_tag = 'end' + token.split_contents()[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()

    return IfSettingNode(arg, nodelist_true, nodelist_false)

class IfSettingNode(Node):
    def __init__(self, arg, nodelist_true, nodelist_false):
        self.arg = arg
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false

    def __repr__(self):
        return "<IfSettingNode>"

    def render(self, context):
        try:
            arg = resolve_variable(self.arg, context)
        except VariableDoesNotExist:
            arg = self.arg
        val = getattr(settings, arg, "")
        if val:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
        