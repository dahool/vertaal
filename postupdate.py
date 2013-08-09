#!/usr/bin/python

import sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import StringIO
import settings
import optparse
import re

version = getattr(settings,'VERSION')
target_path = getattr(settings,'CDN_PATH')
cdn_media_path = 'media/app/vertaal'
source_path = getattr(settings,'STATIC_ROOT')

def copy_media():
    tgt = os.path.join(target_path, cnd_media_path, version)
    if not os.path.exists(tgt):
        os.makedirs(tgt)
    os.system("cp -R %s/* %s" % (source_path, tgt))
    
def upload():
    cmd = 'appcfg.py update %s' % target_path
    if getattr(settings, 'APP_USER',False):
        cmd += ' --email=%s' % settings.APP_USER
    os.system(cmd)
            
def prompt_continue():
    s = "Update cdn version %s?" % version
    r = raw_input(s + " (Y/n): ")
    return not r or r == '' or r.lower() == 'y'
    
def main():
    if prompt_continue():
        copy_media()
        upload()
        
if __name__ == '__main__':
    main()
