import os
import os.path as path
import unittest
import shutil

from django.conf import settings
from common.utils.file import deltree
from projects.models import Project
from languages.models import Language
from files.models import POFile, POTFile
from versioncontrol.manager import Manager, POTUpdater

import StringIO
import sys

class VersionControlTestCase(unittest.TestCase):
    """
    this test will create some garbage
    I dont want to write a deltree function right now
    """
    
    def setUp(self):
        # setup the temp repository using skeleton
        shutil.copytree(getattr(settings, 'TEST_REPO'), getattr(settings, 'TEMP_REPO_PATH'))
            
        # create objects
        self.project = Project.objects.create(name="Project " + getattr(settings, 'PID'),
                                   vcsurl=getattr(settings, 'TEMP_REPO'),
                                   repo_type="svn")
        self.release = self.project.releases.create(name="Repo Test",
                                  vcsbranch="trunk")
        self.component = self.project.components.create(name="Repo Test",
                                  vcspath="test",
                                  potlocation="pot",
                                  format="$PATH/po")
        self.language = Language.objects.create(name="Test",
                                                code="te")
        
#        self.log = logging.getLogger("TEST")
#        self.log.setLevel(logging.INFO)
#        hd = logging.StreamHandler(sys.stdout)
#        self.log.addHandler(hd)
        self.log = sys.stdout
        
    def runTest(self):
        man = Manager(self.project,
                      self.release,
                      self.component,
                      self.language,
                      self.log)

        """ perform checkout """
        # perform build
        rev = man.build()

        # check if the file was added
        pofiles = POFile.objects.filter(component=self.component,
                                  release=self.release,
                                  language=self.language)
        
        # the repo should contain one file only
        self.assertEquals(pofiles.count(),1)
        
        """ perform commit """
        # modify the file
        f = open(pofiles[0].file,"a")
        f.write("test")
        f.close()
        
        # perform commit
        revc = man.commit(None, None, "test")
        self.assertEquals(revc, (rev + 1))
        
        # POT creation
        potman = POTUpdater(self.project, self.release, self.component,self.log)        
        potman.build()
        
        potfiles = POTFile.objects.filter(component=self.component)
        
        self.assertEquals(potfiles.count(),1)
        self.assertEquals(potfiles[0].total,5) # 5 messages
        self.assertEquals(potfiles[0].updated,'2009-09-21 09:47+0200')
        
    def tearDown(self):
        deltree(getattr(settings, 'TEMP_PATH'))