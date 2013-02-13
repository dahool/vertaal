import os
import os.path
import urllib2
import glob

from mercurial import commands, ui, hg
try:
    from mercurial.repo import RepoError # mercurial-1.1.x
except:
    from mercurial.error import RepoError # mercurial-1.2.x

try:
    from mercurial.url import passwordmgr
except:
    from mercurial.httprepo import passwordmgr

from django.utils.translation import ugettext as _

import versioncontrol.lib.browser as browser
from versioncontrol.lib.browser import BrowserException

import logging
logger = logging.getLogger('vertaal.vcs')

def need_repo(fn):
    def repo_fn(self, *args, **kw):
        try:
            self.repo = hg.repository(self.ui, self.location)
        except RepoError:
            self.repo = self.init_repo()
        return fn(self, *args, **kw)
    return repo_fn 

def need_update(fn):
    def repo_fn(self, *args, **kw):
        self.update()
        return fn(self, *args, **kw)
    return repo_fn

def monkeypatch_class(name, bases, namespace):
    assert len(bases) == 1, "Exactly one base class required"
    base = bases[0]
    for name, value in namespace.iteritems():
        if name != "__metaclass__":
            setattr(base, name, value)
    return base

_find_user_password = passwordmgr.find_user_password
user_auth = None

class UserPasswordMgr(passwordmgr):
    __metaclass__ = monkeypatch_class

    def find_user_password(self, realm, authuri):
        global user_auth
        
        authinfo = urllib2.HTTPPasswordMgrWithDefaultRealm.find_user_password(self, realm, authuri)
        theUsername, thePassword = authinfo

        if not hasattr(self, '_cache'):
            self._cache = {}

        theKey = (realm, authuri)
        if theKey in self._cache:
            return self._cache[theKey]

        if not theUsername:
            auth = self.readauthtoken(authuri)
            if auth:
                theUsername, thePassword = auth.get('username'), auth.get('password')
        
        if not theUsername:
            if user_auth:
                theUsername = user_auth.user

        if not thePassword:
            if user_auth:
                thePassword = user_auth.password

            if thePassword:
                self._cache[theKey] = (theUsername, thePassword)

        print theUsername
        print thePassword
        return theUsername, thePassword    
    
class HgBrowser(browser.RepositoryBrowser):
    
    
    
    def __init__(self, location, url, folder, branch='tip', auth=None):
        global user_auth
        # url/branch/folder = http://example.com/branch/folder
        # location = local folder (destination)
        super(HgBrowser, self).__init__(location, url, folder, branch, auth)
        self.ui = ui.ui()
        user_auth = auth
    
    def _process_files(self):
        for file in glob.glob(self.location + "/*.po"):
            self._send_callback(self.callback_on_file_add, file)
    
    @property    
    def _remote_path(self):
        return self.url + self.folder
    
    def init_repo(self):
        logger.debug("init")
        self._send_callback(self.callback_on_action_notify,_('Initializing repository %s') % self._remote_path)

        try:
            logger.debug("Checkout %s on %s" % (self._remote_path, self.location))

            remote_repo, repo = hg.clone(self.ui, self._remote_path, self.location)
            commands.update(repo.ui, repo, self.branch)
            self._process_files()
            logger.debug("end")
        except RepoError, e:
            raise BrowserException, e
        
        # don't know how to get revision number
        return 0

    @need_repo
    def cleanup(self):
        try:
            commands.revert(self.repo.ui, self.repo, date=None, rev=None, 
                            all=True, no_backup=True)
            hg.clean(self.repo, self.branch, show_stats=False)
        except Exception, e:
            logger.error(e)
        
    @need_repo
    def update(self):
        self._send_callback(self.callback_on_action_notify,_('Updating repository %s') % self._remote_path)        
        try:
            self.cleanup()
            commands.pull(self.repo.ui, self.repo, rev=None, force=False, update=True)
            commands.update(self.repo.ui, self.repo, self.branch)
            self._process_files()
        except RepoError, e:
            raise BrowserException, e
        return 0
    
    @need_repo
    def submit(self, auth, msg):
        _user_auth = auth
        logger.debug("Perform submit %s [%s]" % (self.location, msg))
        self._send_callback(self.callback_on_action_notify,_('Checking in'))
        commands.commit(self.repo.ui, self.repo, 
                        message=msg.encode('utf-8'),
                        addremove=True, logfile=None, 
                        date=None)
        commands.push(self.repo.ui, self.repo, force=False, rev=None)
        return 0
