from dateutil.parser import *
import datetime
import re

_CREATION_DATE = re.compile('.(POT-Creation-Date:)[ ](?P<date>[0-9]{4}[-][0-9]{2}[-][0-9]{2}[ ][0-9]{2}[:][0-9]{2}[+|-][0-9]{0,4})')

def extract_creation_date(filename):
    o = open(filename,'r')
    m = None
    for line in o.readlines():
        m = _CREATION_DATE.match(line)
        if m: break
        o.close()
    if m:
        dateval = m.group('date')
        try:
            dt = potdate_to_datetime(dateval)
            return dt
        except Exception, e:
            #logger.error("Date conversion failed (%s)" % str(e))
            pass
    return None

def potdate_to_datetime(value):
    val = parse(value) # dateutil
    t = val.utctimetuple()
    return datetime.datetime(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min)    
