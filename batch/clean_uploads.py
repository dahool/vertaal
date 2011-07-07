import os
import sys

PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
root, path = os.path.split(PATH)
sys.path.append(root)

try:
    execfile(os.path.join(PATH,'setupenv.py'))
except IOError:
    pass

import datetime
from batch.log import (logger)

CLEAN_AGE = getattr(settings, 'BACKUP_CLEAN_AGE', 15)
TODAY = datetime.datetime.today()

def execute():
    logger.info("Start")
    count = 0

    logger.debug("Processing project backup ...")
    for dir in os.walk(settings.UPLOAD_PATH):
        pathname, s, files = dir
        for name in files:
            filename = os.path.join(pathname, name)
            logger.debug("Processing %s" % filename)
            if str.lower(os.path.splitext(filename)[-1]) == '.bak':
                created = datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)
                diff = TODAY - created
                logger.debug("File age is: %s" % diff.days)
                if diff.days > CLEAN_AGE:
                    try:
                        logger.debug("Removing %s" % filename) 
                        os.unlink(filename)
                        count+=1
                    except Exception, e:
                        logger.error(e)
                else:
                    logger.debug("OK")

    logger.debug("Processing user path ...")
    for dir in os.walk(settings.TEMP_UPLOAD_PATH):
        pathname, s, files = dir
        for name in files:
            filename = os.path.join(pathname, name)
            logger.debug("Processing %s" % filename)
            created = datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)
            diff = TODAY - created
            logger.debug("File age is: %s" % diff.days)
            if diff.days > CLEAN_AGE:
                try:
                    logger.debug("Removing %s" % filename) 
                    os.unlink(filename)
                    count+=1
                except Exception, e:
                    logger.error(e)
            else:
                logger.debug("OK")
    logger.info("Removed %d" % count)
    print "Removed %d" % count
    logger.info("End")

if __name__ == '__main__':
    print "Start"
    execute()
    print "End"                   