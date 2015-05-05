#!/usr/bin/python

import sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import StringIO
import settings
import optparse
import re
import shutil
from minmedia import minimizejs

version = getattr(settings,'VERSION')
target_path = getattr(settings,'CDN_PATH')
cdn_media_path = 'media/app/vertaal'
source_path = getattr(settings,'STATIC_ROOT')

def copy_media():
    tgt = os.path.abspath(os.path.join(target_path, cdn_media_path, version))
    if os.path.exists(tgt):
        shutil.rmtree(tgt, ignore_errors=True)
        #os.makedirs(tgt)
    print "Prepare..."
    #os.system("cp -vR %s/* %s" % (source_path, tgt))
    shutil.copytree(source_path, tgt)
    if prompt_min(): minimizejs(tgt)
    
def upload():
    #cmd = 'appcfg.py'
    cmd = 'appcfg'
    if getattr(settings,'APP_TOKEN', False):
        cmd += ' --oauth2_refresh_token=%s' % settings.APP_TOKEN
    else:
        cmd += ' --oauth2 --noauth_local_webserver'
    if getattr(settings, 'APP_USER',False):
        cmd += ' --email=%s' % settings.APP_USER
    cmd += ' update %s' % target_path
    os.system(cmd)

def prompt(s):
    r = raw_input(s + " (Y/n): ")
    return not r or r == '' or r.lower() == 'y'
    
def prompt_continue():
    return prompt("Update cdn version %s?" % version)

def prompt_min():
    return prompt("Minimize JS?")

def main():
    if prompt_continue():
        copy_media()
        if prompt("Upload?"): upload()
        
if __name__ == '__main__':
    main()
