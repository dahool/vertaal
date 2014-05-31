from django.views.decorators.cache import cache_page
from django.conf.urls import patterns, url, include
from django.conf import settings
from appfeeds.feeds import *
from appfeeds.views import common_feed

feeds = {
    'updates': ReleaseUpdates,
    'commit_queue': CommitQueue,
    'file': FileFeed
}

def redirect(request, language):
    from django.core.urlresolvers import reverse
    from django.http import HttpResponsePermanentRedirect
    
    return HttpResponsePermanentRedirect(reverse('language_release_feed',
                                                 kwargs={'slug': 'factory',
                                                         'language': language}))

urlpatterns = patterns('',
#    url(r'^opensuse-11-2/(?P<language>[-_@\w]+)/updates/$', redirect),
    url(r'^(?P<slug>[-\w]+)/(?P<language>[-_@\w]+)/updates/$',
        cache_page(common_feed, getattr(settings, 'FEED_CACHE', 1800)),
        name="language_release_feed",
        kwargs={'feed_slug': 'updates', 'feeds': feeds}),
    url(r'^(?P<slug>[-\w]+)/updates/$',
        cache_page(common_feed, getattr(settings, 'FEED_CACHE', 1800)),
        name="release_feed",
        kwargs={'feed_slug': 'updates', 'feeds': feeds}),
    url(r'^(?P<slug>[-\w]+)/(?P<language>[-_@\w]+)/queue/$',
        cache_page(common_feed, getattr(settings, 'FEED_CACHE', 1800)),
        name="language_project_queue_feed",
        kwargs={'feed_slug': 'commit_queue', 'feeds': feeds}),
    url(r'^(?P<slug>[-\w]+)/queue/$',
        cache_page(common_feed, getattr(settings, 'FEED_CACHE', 1800)),
        name="project_queue_feed",
        kwargs={'feed_slug': 'commit_queue', 'feeds': feeds}),        
    url(r'^(?P<slug>[-\w]+)/file/$',
        cache_page(common_feed, getattr(settings, 'FEED_CACHE', 1800)),
        name="file_feed",
        kwargs={'feed_slug': 'file', 'feeds': feeds}),
)