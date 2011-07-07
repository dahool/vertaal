import os
from os import listdir
from os.path import isdir
from common.utils.commands import get_command_output

PROJECT_PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
MEDIA_PATH = os.path.join(PROJECT_PATH, 'site_media')
JS_PATH = os.path.join(MEDIA_PATH, 'js','src')
CSS_PATH = os.path.join(MEDIA_PATH, 'css')

CMD = 'java -jar yuicompressor.jar --type %(type)s --charset utf-8 %(file)s'
 
out = []
for file in listdir(JS_PATH):
    if not isdir(file):
        print "Processing %s" % file
        cmd = CMD % {'type': 'js', 'file': os.path.join(JS_PATH, file)}
        out.append("".join(get_command_output(cmd)))

res = "\n".join(out)
print res
dest = open('application.js','w')
dest.write(res)
dest.close()
