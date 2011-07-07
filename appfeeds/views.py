from django.contrib.syndication.views import feed

def common_feed(request, slug, language = None, feed_slug = None, feeds = {}):
    
    if language:
        param = '%s/%s' % (slug, language)
    else:
        param = slug
    
    url = "%s/%s" % (feed_slug, param)

    return feed(request, url, feeds)