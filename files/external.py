from django.conf import settings
from app.log import (logger)
import os
import shutil

def is_enabled():
    return getattr(settings,'FILE_EXTERNAL_URL', None) and getattr(settings,'FILE_EXTERNAL_PATH', None)
    
def get_file_location(elem):
    from files.models import POFile, POTFile, POFileSubmit
    url = []
    if isinstance(elem, POFileSubmit):
        pofile = elem.pofile
    else:
        pofile = elem
    url.append(pofile.release.project.slug)
    url.append(pofile.release.slug)
    url.append(pofile.component.slug)
    if isinstance(elem, POFileSubmit):
        url.append('SUBMIT')
        url.append(elem.pofile.filename)
    elif isinstance(elem, POTFile):
        url.append('POT')
        url.append(elem.name)
    else:
        url.append(elem.filename)
    return url
    
def get_external_url(elem):
    if is_enabled():
        return settings.FILE_EXTERNAL_URL + '/'.join(get_file_location(elem))
    else:
        return None
        
def update_file_handler(sender, instance, created, **kw):
    tgtfile = os.path.join(settings.FILE_EXTERNAL_PATH, os.path.sep.join(get_file_location(instance)))
    try:
        if not os.path.exists(os.path.dirname(tgtfile)):
            os.makedirs(os.path.dirname(tgtfile))
        logger.debug('Update ' + tgtfile)
        shutil.copy(instance.handler.get_file_path(), tgtfile)
    except Exception, e:
        logger.error(str(e))

def remove_file_handler(sender, instance, **kw):
    tgtfile = os.path.join(settings.FILE_EXTERNAL_PATH, os.path.sep.join(get_file_location(instance)))
    if os.path.exists(tgtfile):
        try:
            logger.debug('Delete ' + tgtfile)
            os.remove(tgtfile)
        except Exception, e:
            logger.error(str(e))
