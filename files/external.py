from django.conf import settings
from app.log import (logger)
import os
import shutil

def is_enabled():
    return getattr(settings,'FILE_EXTERNAL_URL', None) and getattr(settings,'FILE_EXTERNAL_PATH', None)
    
def get_file_location(elem):
    from files.models import POFile, POTFile, POFileSubmit
    name = None
    url = []
    if isinstance(elem, POFileSubmit):
        pofile = elem.pofile
    else:
        pofile = elem
    url.append(pofile.release.project.slug)
    url.append(pofile.release.slug)
    if isinstance(elem, POFileSubmit):
        url.append('SUBMIT')
        url.append("%s_%s" % (elem.pk, elem.pofile.filename))
        name = elem.pofile.filename
    elif isinstance(elem, POTFile):
        url.append(pofile.component.slug)
        url.append('POT')
        url.append(elem.name)
    else:
        url.append(pofile.component.slug)
        url.append(elem.filename)
    return name, url
    
def get_external_url(elem):
    if is_enabled():
        name, url = get_file_location(elem)
        exurl = settings.FILE_EXTERNAL_URL + '/'.join(url)
        if name:
            exurl = exurl + "?name=" + name
        return exurl
    elif getattr(settings,'FILE_DIRECT_URL', None):
        from files.models import POFileSubmit
        if isinstance(elem, POFileSubmit):
            target = os.path.join(settings.TEMP_UPLOAD_PATH, elem.pofile.slug, elem.pofile.filename)
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
                os.chmod(os.path.dirname(target), int('755',8))
            shutil.copy(elem.handler.get_file_path(), target)
            basepath = target
        else:
            basepath = elem.handler.get_file_path()
        location = basepath.replace(settings.ROOT_PATH,settings.FILE_DIRECT_URL).replace('\\','/')
        return location
    else:
        return None
        
def update_file_handler(sender, instance, created, **kw):
    name, url = get_file_location(instance)
    tgtfile = os.path.join(settings.FILE_EXTERNAL_PATH, os.path.sep.join(url))
    try:
        if not os.path.exists(os.path.dirname(tgtfile)):
            os.makedirs(os.path.dirname(tgtfile))
        logger.debug('Update ' + tgtfile)
        shutil.copy(instance.handler.get_file_path(), tgtfile)
    except Exception, e:
        logger.error(str(e))

def remove_file_handler(sender, instance, **kw):
    name, url = get_file_location(instance)
    tgtfile = os.path.join(settings.FILE_EXTERNAL_PATH, os.path.sep.join(url))
    if os.path.exists(tgtfile):
        try:
            logger.debug('Delete ' + tgtfile)
            os.remove(tgtfile)
        except Exception, e:
            logger.error(str(e))
