from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from django.contrib.auth.models import User
from projects.models import Project
from languages.models import Language
import itertools

SUBMISSION_TYPE = (
    (0, _('Review all submits')),
    (1, _('Allow users to submit to repository')),
)
                    
class TeamUser(User):
    
    def __init__(self, instance):
        self.__dict__.update(instance.__dict__)
        
    class Meta:
        proxy = True

    @property
    def is_coord(self):
        return False
    
    @property
    def is_committer(self):
        return False
    
    @property
    def last_activity(self):
        try: 
            latest = self.pofilelog_set.latest().created
            if latest > self.last_login:
                return latest
        except:
            pass
        return self.last_login

class CommiterUser(TeamUser):
    
    class Meta:
        proxy = True
    
    @property
    def is_committer(self):
        return True

class CoordinatorUser(TeamUser):
    
    class Meta:
        proxy = True
    
    @property
    def is_coord(self):
        return True

class ProxyIterator:
    
    def __init__(self, proxyModel, querySet):
        self.proxyModel = proxyModel
        self.querySet = querySet
        
    def __iter__(self):
        for obj in self.querySet:
            yield self.proxyModel(obj)
    
class HasheableTeam:
    
    language = None
    project = None
    
    def __init__(self, language, project):
        self.language = language
        self.project = project
        
    def __hash__(self):
        return self.language.__hash__() + self.project.__hash__() + 99
    
    def __eq__(self, other):
        try:
            return self.language == other.language and self.project == other.project
        except:
            return False
        
class Team(models.Model):

    language = models.ForeignKey(Language, related_name='teams')
    project = models.ForeignKey(Project, related_name='teams')
    coordinators = models.ManyToManyField(User, related_name='team_coordinator',
                                         blank=True, null=True)
    committers = models.ManyToManyField(User, related_name='committer',
                                        blank=True, null=True)
    members = models.ManyToManyField(User, related_name='team_member',
                                         blank=True, null=True)
    submittype = models.IntegerField(default=0, db_index=True, choices=SUBMISSION_TYPE)
    
    def __unicode__(self):
        return u'%s (%s)' % (self.project.name, self.language.name)

    def __repr__(self):
        return u'<Team: %(project)s (%(language)s)>' % {'project':self.project.name, 'language':self.language.name}
    
    class Meta:
        db_table = 'teams'
        unique_together = ("language", "project")
        permissions = (
                    ("can_commit", "Can submit files to repository"),
                )
        
    def can_manage(self, user):
        if (self.project.is_maintainer(user) 
                or (user in self.coordinators.all())):
            return True
        return False
    
    def can_commit(self, user):
        return (user in self.committers.all() or self.can_manage(user))

    def is_member(self, user):
        return (user in self.members.all() or
            user in self.committers.all() or
            user in self.coordinators.all())
    
    def remove_member(self, user):
        if user in self.committers.all():
            self.committers.remove(user)
        elif user in self.members.all():
            self.members.remove(user)
        else:
            self.coordinators.remove(user)

    @property
    def list_coordinators(self):
        '''Returns a proxy user instead of the original model.
        This is because the proxies in django are not implemented as it should be
        and the parent model is not taken into account when the relation ship is done
        '''
        return ProxyIterator(CoordinatorUser, self.coordinators.all())

    @property
    def list_commiters(self):
        '''Returns a proxy user instead of the original model.
        This is because the proxies in django are not implemented as it should be
        and the parent model is not taken into account when the relation ship is done
        '''
        return ProxyIterator(CommiterUser, self.committers.all())

    @property
    def list_members(self):
        '''Returns a proxy user instead of the original model.
        This is because the proxies in django are not implemented as it should be
        and the parent model is not taken into account when the relation ship is done
        '''
        return ProxyIterator(TeamUser, self.members.all())
    
    @property
    def team_members(self):
        '''this method execute the query in db'''
        return itertools.chain(self.list_coordinators, self.list_commiters, self.list_members)
    
    @permalink
    def get_absolute_url(self):
        return ('team_detail', None, { 'project': self.project.slug, 'lang': self.language.code })
         
class JoinRequest(models.Model):
    
    user = models.ForeignKey(User)
    team = models.ForeignKey(Team, related_name="join_requests")
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return _(u'<User: %(user)s - Team: %(project)s (%(language)s)>') % {'user': self.user,
                                                                            'project':self.team.project.name,
                                                                            'language':self.team.language.name}

    def __repr__(self):
        return '<User: %(user)s - Team: %(project)s (%(language)s)>' % {'user': self.user,
                                                                        'project':self.team.project.name,
                                                                        'language':self.team.language.name}
    
    class Meta:
        db_table = 'join_requests'
        unique_together = ("user", "team")
