from django import template
from django.utils.encoding import force_unicode

register = template.Library()

@register.filter
def sum_trans_fuzzy(stat):
    """
    This filter returns a sun of the translated and fuzzy percentages
    """
    return (stat.trans_perc + stat.fuzzy_perc) 