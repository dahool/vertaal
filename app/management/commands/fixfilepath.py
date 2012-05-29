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
from versioncontrol.manager import get_repository_path, normalize_path, get_potrepository_path
from batch.log import (logger)
from projects.models import Project
from files.models import POFile

class Command(BaseCommand):
    help = 'File file absolute paths'

    def handle(self, *args, **options):
        self.stdout.write('Started.\n')
        logger.info("Start")
        t_start = time.time() 

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
                            pofile.file = normalize_path(basepath, pofile.file)
                            pofile.save()
                            try:
                                pot = pofile.potfile.get()
                                pot.file = normalize_path(potbasepath, pot.file)
                                pot.save()
                            except:
                                pass

        logger.info("End")
        self.stdout.write('Completed in %d seconds.\n' % int(time.time() - t_start))