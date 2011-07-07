#!/usr/bin/env python
import MySQLdb
from django.conf import settings

_QUERY = 'ALTER TABLE pofile add column potupdated DATETIME NULL DEFAULT NULL'

conn = MySQLdb.connect(host=settings.DATABASE_HOST or 'localhost',
                user=settings.DATABASE_USER,
                passwd=settings.DATABASE_PASSWORD,
                db=settings.DATABASE_NAME)

cursor = conn.cursor()
cursor.execute(_QUERY)
cursor.close()

conn.commit()
conn.close()
  