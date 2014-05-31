from django.conf.urls import patterns, url
from appfeeds.feeds import *
from appfeeds.views import common_feed

feeds = {
    'updates': ReleaseUpdates,
    'commit_queue': CommitQueue,
    'file': FileFeed
}

def redirect(request, language):
    from django.http import HttpResponsePermanentRedirect
    
    return HttpResponsePermanentRedirect(reverse('language_release_feed',
                                                 kwargs={'slug': 'factory',
                                                         'language': language}))

urlpatterns = patterns('',
#    url(r'^opensuse-11-2/(?P<language>[-_@\w]+)/updates/$', redirect),
    url(r'^(?P<slug>[-\w]+)/(?P<language>[-_@\w]+)/updates/$',
        common_feed,
        name="language_release_feed",
        kwargs={'feed_slug': 'updates', 'feeds': feeds}),
    url(r'^(?P<slug>[-\w]+)/updates/$',
        common_feed,
        name="release_feed",
        kwargs={'feed_slug': 'updates', 'feeds': feeds}),
    url(r'^(?P<slug>[-\w]+)/(?P<language>[-_@\w]+)/queue/$',
        common_feed,
        name="language_project_queue_feed",
        kwargs={'feed_slug': 'commit_queue', 'feeds': feeds}),
    url(r'^(?P<slug>[-\w]+)/queue/$',
        common_feed,
        name="project_queue_feed",
        kwargs={'feed_slug': 'commit_queue', 'feeds': feeds}),        
    url(r'^(?P<slug>[-\w]+)/file/$',
        common_feed,
        name="file_feed",
        kwargs={'feed_slug': 'file', 'feeds': feeds}),
)