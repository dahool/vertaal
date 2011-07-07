import unittest
from projects.models import Project

class ProjectTestCase(unittest.TestCase):
    
    test_repo_pass = "a_project_password"
    
    def setUp(self):
        p = Project(name="Project Test")
        p.set_repo_pwd(self.test_repo_pass)
        p.save()
        
        p = Project(name="Project Test 2")
        p.enabled = False
        p.save()
    
    def runTest(self):
        p = Project.objects.get(slug="project-test")
        self.assertEquals(repr(p),"<Project: Project Test>")
        self.assertEquals(p.get_repo_pwd(),self.test_repo_pass)
        self.assertEquals(p.objects.by_authorized().count(),1)