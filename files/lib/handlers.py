import os
import shutil
import tarfile
import tempfile
import time

from django.db import transaction
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from django.conf import settings
from common.utils.file import deltree
from files.lib.msgfmt import *
from files.models import POFile,POFileSubmit,POFileLog,LOG_ACTION, SUBMIT_STATUS_ENUM

import logging
logger = logging.getLogger(__name__)
                      
class LockedException(Exception):
    pass
    
def find_matching_file(name, release, language, user):
    files = POFile.objects.filter(filename__iexact=name,
                                  release=release,
                                  language=language,
                                  locks__owner=user)
    logger.debug("Match files for '%s': %d" % (name,files.count()))
    if files.count() == 0:
        files = POFile.objects.filter(filename__iexact=name,
                                      release=release,
                                      language=language)
        if files.count()>0:
            raise Exception,  _('You should lock the file %s before upload it.' % name)
        else:
            raise Exception, _("Couldn't find a matching file for %s." % name)
    elif files.count()>1:
        raise Exception, _("Found more than one file matching filename %s.") % name
    else:
        return files[0]
#    else:
#        for f in files:
#            if f.locked:
#                if f.locks.get().owner.username == user.username:
#                    return f
#        raise Exception, _('You should lock the file prior to submit it.')
        
def handle_text_file(pofile, text, user, comment=''):
    logger.debug("Enter")
    dest_path = os.path.join(settings.TEMP_UPLOAD_PATH, user.username)
    logger.debug("Path is %s" % dest_path)
    if not os.path.exists(dest_path):
        logger.debug("Creating path")
        os.makedirs(dest_path)
    dest_file = os.path.join(dest_path, pofile.slug + ".po")
    logger.debug("Saving file ...")
    try:
        dest = open(dest_file, 'w')
        dest.write(text.encode("utf-8"))
        dest.close()
    except Exception, e:
        logger.error(e)
        raise
    check_file(dest_file, pofile.language.code, pofile)
    new_file = get_upload_path(pofile)
    move_file(dest_file, new_file)
    try:
        r = add_submit(pofile, user, new_file, comment)
    except Exception, e:
        try:
            os.unlink(new_file)
        except:
            pass
        raise e
    return r

def move_file(src, tge):
    logger.debug("Move file")
    try:
        if not os.path.exists(os.path.dirname(tge)):
            logger.debug("Create directory structure")
            os.makedirs(os.path.dirname(tge))
    except:
        logger.debug("Failed creating directory structure")
        pass
    logger.debug("Copy %s to %s" % (src,tge))
    shutil.copy2(src, tge)
    while not os.path.exists(tge):
        logger.debug("Copy fail")
        shutil.copy2(src, tge)
    os.chmod(src, getattr(settings, 'FILE_UPLOAD_PERMISSIONS',0664))  
    os.chmod(tge, getattr(settings, 'FILE_UPLOAD_PERMISSIONS',0664))        
    if not getattr(settings, 'BACKUP_UPLOADS',False):
        try:
            logger.debug("Remove source")
            os.remove(src)
        except:
            logger.debug("Failed to remove")
            pass
    
def get_upload_path(pofile, appendfile = True):
    """
        returns the upload path + filename
    """
    upath = os.path.join(settings.UPLOAD_PATH,pofile.component.project.slug)
    if appendfile:
        upath = os.path.join(upath, "%s_%s.po" % (str(int(time.time())), pofile.slug))
    return upath
    
def add_submit(pofile, owner, temp_file, comment='', merge=True):
    posubmit = None
    try:
        posubmit = sub = POFileSubmit.objects.get(pofile=pofile, status=SUBMIT_STATUS_ENUM.PENDING)
        if sub.locked:
            raise LockedException, _("%(file)s is being processed. It can't be modified right now.") % {'file': pofile.filename}
        sub.update(owner=owner, file=temp_file, log_message=comment)
        sub.save()
        newsubmit = False
    except POFileSubmit.DoesNotExist:
        posubmit = POFileSubmit.objects.create(pofile=pofile, owner=owner, file=temp_file, log_message=comment, merge=merge, status=SUBMIT_STATUS_ENUM.PENDING)
    except LockedException:
        raise
    except Exception, e:
        logger.error("Add submit failed [%s]" % smart_unicode(e))
        raise Exception, _("Failed [%s]. Please try again. If the problem persist fill a ticket.") % smart_unicode(e)
    log = POFileLog.objects.create(pofile=pofile, user=owner, action=LOG_ACTION['ACT_UPLOAD'], comment=comment)
    return posubmit
        
def check_file(temp_file, lang, pofile = None):
    logger.debug("Check file %s" % temp_file)
    try:
        msgfmt_check(temp_file, lang)
        logger.debug("Check OK")
#        if pofile:
#            pot = pofile.potfile
#            if pot:
#                stats = get_file_stats(temp_file)
#                total = stats['translated']+stats['untranslated']+stats['fuzzy']
#                if total != pot.total:
#                    raise Exception(_('The file %(filename)s doesn\'t match the current POT file. Please, download the file again and try a manual merge.') % {'filename': pofile.filename})
    except Exception, e:
        logger.debug("Check FAILED")
        try:
            os.remove(temp_file)
        except:
            pass
        raise e
            
def handle_uploaded_file(file, release, language, user, comment='', pofile=None):
    #we need to check first if it's tared
    logger.debug("Handle upload %s" % file)
    tmpfile = None
    try:
        #lets create a temporary physical file first
        tmpdir = os.path.join(settings.TEMP_UPLOAD_PATH, user.username)
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)
        tmpid, tmpfile = tempfile.mkstemp(dir=tmpdir)
        logger.debug("Created temp file %s" % tmpfile)
        dest = open(tmpfile,'wb+')
        for chunk in file.chunks():
            dest.write(chunk)
        dest.close()
        #tared = tarfile.open(fileobj=file)
        tared = tarfile.open(name=tmpfile)
    except IOError, e:
        logger.error(e)
        raise Exception, _("Unable to open the file %s.") % file
    except OSError, e:
        logger.error(e)
        raise Exception, _("Unable to open the file %s.") % file
    except tarfile.ReadError:
        #the file is not tared
        if not pofile:
            pofile = find_matching_file(file.name, release, language, user)
        else:
            if not pofile.filename == file.name:
                raise Exception, _("You are supposed to upload a new version of %(expected)s, instead we found %(uploaded)s.") % {'expected': pofile.filename, 'uploaded': file.name}
#        dest_path = os.path.join(settings.TEMP_UPLOAD_PATH, user.username)
#        if not os.path.exists(dest_path):
#            os.makedirs(dest_path)
#        dest_file = os.path.join(dest_path, pofile.slug + ".po")
#        dest = open(dest_file, 'wb+')
#        for chunk in file.chunks():
#            dest.write(chunk)
#        dest.close()
#        check_file(dest_file, pofile.language.code, pofile)
#        new_file = get_upload_path(pofile)
#        move_file(dest_file, new_file)
        check_file(tmpfile, pofile.language.code, pofile)
        new_file = get_upload_path(pofile)
        move_file(tmpfile, new_file)
        #if os.path.exists(new_file):
        return [add_submit(pofile, user, new_file, comment)]
        #raise Exception, _("Failed to copy file %s. Please try again." % pofile)
    except Exception, e:
        logger.error(e)
        raise        
    else:
        # check if contains directory entries
        for tf in tared.getnames():
            if tf.find('/') != -1:
                raise Exception, _("The tar file should not contain any directories.")
        
        pofiles = []
        for tf in tared.getnames():
            pofiles.append(find_matching_file(tf, release, language, user))
        tempdir = tempfile.mkdtemp(prefix=file.name, dir=tmpdir)
        tared.extractall(path=tempdir)
        tared.close()
        
        for pf in pofiles:
            check_file(os.path.join(tempdir,pf.filename), pf.language.code, pf)
        
        transaction.enter_transaction_management()
        transaction.managed(True)
        submits = []
        try:
            for pf in pofiles:
                new_file = get_upload_path(pf)
                move_file(os.path.join(tempdir, pf.filename), new_file)
                submits.append(add_submit(pf, user, new_file, comment))
        except:
            transaction.rollback()
            logger.debug("Transaction rolledback")
            raise
        else:
            transaction.commit()
            logger.debug("Transaction commited")
        finally:
            logger.debug("Delete all")
            deltree(tempdir)
            logger.debug("Leave transaction")            
            transaction.leave_transaction_management()
        return submits        
    finally:
        #delete temp file
        if tmpfile:
            try:
                os.unlink(tmpfile)
            except:
                pass
            
def process_merge(pofile, user):

    try:
        new_file = get_upload_path(pofile)
    
        if not os.path.exists(os.path.dirname(new_file)):
            os.makedirs(os.path.dirname(new_file))
        
        # update the file first
        pofile.handler.update_repo()
        out = msgmerge(pofile.file, pofile.potfile.get().file, new_file)

    except Exception, e:
        logger.error(e)
        raise Exception, _('An error occurred while performing file merge. %s' % str(e))        
#        
    if len(out)>1:
        logger.error(";".join(out))
        raise Exception, _('An error occurred while performing file merge. %s' % ";".join(out)) 

    return add_submit(pofile, user, new_file, _('Merged.'), merge=False)
