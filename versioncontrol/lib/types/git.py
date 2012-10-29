'''This git implementation is based on the one from Transifex
'''
import os
import os.path

from django.utils.translation import ugettext as _

import versioncontrol.lib.browser as browser
from app.log import (logger)
from git import *
from git.exc import InvalidGitRepositoryError, NoSuchPathError

def need_repo(fn):
    def repo_fn(self, *args, **kw):
        try:
            r = Repo(self.location)
        except InvalidGitRepositoryError:
            self.init_repo()
        return fn(self, *args, **kw)
    return repo_fn 

def need_update(fn):
    def repo_fn(self, *args, **kw):
        self.update()
        return fn(self, *args, **kw)
    return repo_fn

class GitBrowser(browser.RepositoryBrowser):

    def __init__(self, location, url, folder, branch='master', auth=None):
        super(GitBrowser, self).__init__(location, url, folder, branch, auth)
        
        self.location = os.path.normpath(os.path.normcase(location))
            
    def init_repo(self):
        """ initialize repository
        """
        logger.debug("init")
        self._send_callback(self.callback_on_action_notify,_('Initializing repository %s') % self.url)
        
        repo = Repo.clone_from(self.url, self.location)
        
    @need_repo        
    def cleanup(self):
        """ cleanup any pending operation
        """
        
    @need_repo    
    def update(self):
        """ perform update
        """
        r.remote.pull()
        
    @need_repo
    def submit(self, auth = None, msg):
        """ commit the files
            requires a BrowserAuth instance
        """
        repo = Repo(self.location)
        if repo.is_dirty():
            repo.index.add([*]) #<---
            rev = repo.index.commit(msg)
            repo.remote().push()
            return rev.name_rev
        return None