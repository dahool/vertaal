#!/usr/bin/env python
import MySQLdb
from django.conf import settings

_QUERY = "ALTER TABLE pofile_submit DROP INDEX pofile_id"

dbsettings = settings.DATABASES['default']
conn = MySQLdb.connect(host=dbsettings['HOST'] or 'localhost',
                user=dbsettings['USER'],
                passwd=dbsettings['PASSWORD'],
                db=dbsettings['NAME'])

cursor = conn.cursor()
cursor.execute(_QUERY)
cursor.close()

conn.commit()
conn.close()
