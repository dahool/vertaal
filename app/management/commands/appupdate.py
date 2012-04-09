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
from __future__ import with_statement
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from vertaalevolve.models import AppVersion

class Command(BaseCommand):
    help = 'Apply App Changes'

    def apply_update(self, ver):
        try:
            filename = os.path.join(settings.PROJECT_PATH,'vertaalevolve','updates','ver_' + ver.replace('.','_') + ".py")
            av = AppVersion.objects.get(version=ver)
        except AppVersion.DoesNotExist:
            if os.path.exists(filename):
                self.stdout.write("Apply version patch %s\n" % ver)
                try:
                    execfile(filename)
                except IOError, e:
                    print e          
                else:
                    AppVersion.objects.create(version=ver)
            else:
                self.stdout.write("No updates available for %s\n" % ver)
                AppVersion.objects.create(version=ver)
        else:
            self.stdout.write("Version %s is ok\n" % ver)
        
        
    def handle(self, *args, **options):

        self.stdout.write('Executing update.\n')
        
        for ver in settings.VERSION_HIST:
            self.apply_update(ver);
        # CURRENT
        self.apply_update(settings.VERSION);
        self.stdout.write("Done.\n");