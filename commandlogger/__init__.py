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
