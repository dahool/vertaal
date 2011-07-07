#!/usr/bin/python
import sys
import os
import tarfile
import time
import datetime

SENDMAIL = "/usr/sbin/sendmail" 
MYSQLDUMP = "/usr/bin/mysqldump"

PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
root, path = os.path.split(PATH)
sys.path.append(root)

try:
    execfile(os.path.join(PATH,'setupenv.py'))
except IOError:
    pass

username = settings.DATABASE_USER
password = settings.DATABASE_PASSWORD
database = settings.DATABASE_NAME
host = settings.DATABASE_HOST or 'localhost'
path = os.path.join(settings.ROOT_PATH,'backup')

if not os.path.exists(path):
    os.mkdir(path)

os.chdir(path)

filename = database + "_" + datetime.datetime.now().strftime('%Y%m%d%H%M') + ".sql"

print "Creating ", filename

command = MYSQLDUMP + " --user=" + username + " --password=" + password + " -B " + database + " -h " + host + " --add-drop-table -c -C -e -K -n --add-locks -q --result-file=" + filename
os.system(command)

print "Compressing "

tarname = filename + ".tar.gz"
tar = tarfile.open(tarname,"w:gz")
tar.add(filename);
tar.close();

os.remove(filename)

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

def sendMail(to, subject, text, files=[],server="localhost"):
    assert type(to)==list
    assert type(files)==list
    fro = settings.DEFAULT_FROM_EMAIL

    msg = MIMEMultipart()
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % os.path.basename(file))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(fro, to, msg.as_string() )
    smtp.close()

sendMail(
        ["gabriel.sgt@gmail.com"],
        "DB BACKUP [" + filename + "]","",
        [tarname]
    )