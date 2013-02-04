from django import template
from django.conf import settings
from django.utils.encoding import force_unicode
from news.models import Article

register = template.Library()

@register.inclusion_tag('news/latest.html')
def latest_news():
    return {'news': Article.objects.all_active().order_by("-created")[:getattr(settings, 'LATEST_NEWS',10)]}