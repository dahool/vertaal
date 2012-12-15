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
from django.core.management.base import BaseCommand
import time
import os
from versioncontrol.manager import get_repository_path, normalize_path, get_potrepository_path
from batch.log import (logger)
from projects.models import Project
from files.models import POFile
from files.lib.handlers import get_upload_path
from django.utils.encoding import smart_unicode
from django.conf import settings

class Command(BaseCommand):
    help = 'Relocate files to new repository location'

    def handle(self, *args, **options):
        self.stdout.write('Started.\n')
        logger.info("Start")
        t_start = time.time() 

        total = POFile.objects.count()
        proc = 0
        projects = Project.objects.all()
        for project in projects:
            self.stdout.write('Processing %s.\n' % project.name)
            teams = project.teams.all()
            for release in project.releases.all():
                for component in project.components.all():
                    for team in teams:
                        basepath = get_repository_path(project, release, component, team.language)
                        potbasepath = get_potrepository_path(project, release, component)
                        for pofile in POFile.objects.filter(release=release, component=component, language=team.language):
                            pofile.file = os.path.join(settings.REPOSITORY_LOCATION,normalize_path(basepath, pofile.file)).replace('\\','/')
                            pofile.save()
                            proc += 1
                            try:
                                pot = pofile.potfile.get()
                                pot.file = os.path.join(settings.REPOSITORY_LOCATION, normalize_path(potbasepath, pot.file)).replace('\\','/')
                                pot.save()
                            except:
                                pass
                            for pofilesubmit in pofile.submits.all():
                                try:
                                    upath = get_upload_path(pofile, False)
                                    upath = os.path.join(upath, os.path.basename(smart_unicode(pofilesubmit.file)))
                                    pofilesubmit.file = upath.replace('\\','/')
                                    pofilesubmit.save()
                                except:
                                    pass                            
                        self.stdout.write('Completed %s %%...\n' % str((proc * 100) / total))

        logger.info("End")
        self.stdout.write('Completed in %d seconds.\n' % int(time.time() - t_start))
