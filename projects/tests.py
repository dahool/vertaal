# -*- coding: utf-8 -*-
"""Copyright (c) 2012 Sergio Gabriel Teves
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
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