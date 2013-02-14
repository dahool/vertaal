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
from models import CommandLog

class LogBaseCommand(BaseCommand):
    
    def _getname(self):
        return str(self.__class__).split('.')[-2]
    
    def handle(self, *args, **options):
        cmd = CommandLog(command=self._getname())
        try:
            rsp = self.do_handle(*args, **options)
            if rsp:
                cmd.response = rsp
        except Exception, e:
            cmd.success = False
            cmd.exception = str(e)
            raise
        finally:
            cmd.save()
    
    def do_handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement
        this method.

        """
        raise NotImplementedError()
