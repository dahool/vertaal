from django.contrib.syndication.views import Feed
from django.views.decorators.cache import cache_page

@cache_page(60 * 360)
def common_feed(request, slug, language = None, feed_slug = None, feeds = {}):
    
    if language:
        param = '%s/%s' % (slug, language)
    else:
        param = slug
    
    url = "%s/%s" % (feed_slug, param)

    return Feed(request, url, feeds)