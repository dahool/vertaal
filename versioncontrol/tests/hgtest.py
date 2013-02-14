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
import sys

sys.path.append("Y:\\grwks\\vertaal")

from django.core.management import setup_environ
import sys

try:
    import settings
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

setup_environ(settings)

from versioncontrol.lib.types import hg
from versioncontrol.lib.browser import BrowserAuth

a = BrowserAuth("vertaal", "coyote")

browser = hg.HgBrowser(location="y:\\temprepo\\testep",
                       url="http://bitbucket.org/vertaal/hgtest",
                       folder="",
                       branch=".",
                       auth=a)

browser.init_repo()
