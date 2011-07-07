from django.contrib.syndication.feeds import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from files.models import POFileLog, POFileSubmit, POFile
from projects.models import Project
from releases.models import Release
from languages.models import Language

#site_name = getattr(settings, 'PROJECT_NAME','')
 
class ReleaseUpdates(Feed):

    total_feeds = 50
    
    def get_object(self, bits):
        '''
            bits[0] => release slug
            bits[1] => lang code
        '''
        if len(bits) == 0:
            raise ObjectDoesNotExist
        release_slug = bits[0]
        release = Release.objects.get(slug=release_slug)
        if not release.enabled or not release.project.enabled:
            raise ObjectDoesNotExist
        try:
            lang_code = bits[1]
            self.language = get_object_or_404(Language, code=lang_code)
        except IndexError:
            self.language = None
        
        if "user" in self.request.GET:
            self.user = User.objects.get(username=self.request.GET['user'])
        else:
            self.user = None
        return release
    
    def title(self, release):
        if self.language:
            return _("%(project)s: Release %(release)s :: %(language)s") % {
                'project': release.project.name,
                'language': self.language.name,
                'release': release.name,}
        else:
            return _("%(project)s: Release %(release)s") % {
                'project': release.project.name,
                'release': release.name,}
            
    def description(self, release):
        if self.language:
            return _("Latest actions for %(language)s language in "
                     "release %(release)s.") % {
                        'language': self.language.name,
                        'release': release.name,}
        else:
            return _("Latest actions in release %(release)s.") % {
                        'release': release.name,}
            
    def link(self, release):
        if not release:
            raise FeedDoesNotExist
        if self.language:
            return reverse('list_files',
                             kwargs={ 'release': release.slug,
                                      'language': self.language.code})
        else:
            return release.get_absolute_url()

    def items(self, release):
        #if self.language:
            ##return POFileLog.objects.filter(pofile__release=release, pofile__language=self.language)[:self.total_feeds]
        return POFileLog.objects.distinct_actions(user=self.user, release=release, language=self.language, limit=self.total_feeds)
        #else:
            ##return POFileLog.objects.filter(pofile__release=release)[:self.total_feeds]
            #return POFileLog.objects.distinct_actions(release=release, limit=self.total_feeds)

    def item_pubdate(self, item):
        return item.created
        
    def item_link(self, item):
        link = '%s?%s#%s' % (reverse('list_files', kwargs={ 'release': item.pofile.release.slug,
                                     'language': item.pofile.language.code}),
                                     item.id,
                                     item.pofile.slug)
        return link
 
class CommitQueue(Feed):

    def get_object(self, bits):
        '''
            bits[0] => project slug
            bits[1] => lang code
        '''
        if len(bits) == 0:
            raise ObjectDoesNotExist
        project_slug = bits[0]
        project = Project.objects.get(slug=project_slug)
        if not project.enabled:
            raise ObjectDoesNotExist
        try:
            lang_code = bits[1]
            self.language = get_object_or_404(Language, code=lang_code)
        except IndexError:
            self.language = None
        return project
    
    def title(self, project):
        if self.language:
            return _("Submission queue status for %(project)s :: %(language)s") % {
                'project': project.name,
                'language': self.language.name,}
        else:
            return _("Submission queue status for %(project)s") % {
                'project': project.name,}
            
    def description(self, project):
        return _("Files in the submission queue.")
            
    def link(self, project):
        if not project:
            raise FeedDoesNotExist
        return reverse('commit_queue')
        
    def items(self, project):
        if self.language:
            return POFileSubmit.objects.by_project_and_language(project, self.language)
        else:
            return POFileSubmit.objects.filter(project=project, enabled=True)

    def item_pubdate(self, item):
        return item.created
        
    def item_link(self, item):
        link = '%s?%s' % (reverse('commit_queue'),
                          item.id)
        return link
    
class FileFeed(Feed):

    def get_object(self, bits):
        '''
            bits[0] => slug
        '''
        if len(bits) == 0:
            raise ObjectDoesNotExist
        slug = bits[0]
        pofile = get_object_or_404(POFile, slug=slug)
        return pofile
    
    def title(self, pofile):
        return _("%(file)s ::  %(project)s %(release)s") % {
                                                  'file': pofile.filename,
                                                  'release': pofile.release.name,
                                                  'project': pofile.release.project.name}
            
    def description(self, pofile):
        return _("Latest actions for %(file)s in %(project)s %(release)s") % {
                                                                  'file': pofile.filename,
                                                                  'release': pofile.release.name,
                                                                  'project': pofile.release.project.name}
            
    def link(self, pofile):
        if not pofile:
            raise FeedDoesNotExist
        return reverse('file_detail', kwargs={'slug': pofile.slug})
        
    def items(self, pofile):
        return pofile.log.all()

    def item_pubdate(self, item):
        return item.created
        
    def item_link(self, item):
        return reverse('file_detail', kwargs={'slug': item.pofile.slug})