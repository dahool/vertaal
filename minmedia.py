import os
from os import listdir
from os.path import isdir
from common.utils.commands import get_command_output

JS_FILES = ['base.js','djangopm.js','filedetail.js','filelist.js','filesubmit.js','jquery.alerts.src.js','jquery.fileupload.js','jquery.iframe-transport.js',
'jquery.json.js','jquery.loading.js','jquery.measure.js','jquery.place.js','jquery.pulse.js','jquery.tablesorter.js','jquery.ui.draggable.js',
'multiselectbox.js','orbited.js','profileapp.js','simpletooltip.js','simpletooltip2.js','stomp.js']

CMD = 'java -jar yuicompressor-2.4.8.jar --nomunge --type %(type)s -o %(file)s --charset utf-8 %(file)s'

def minimizejs(path):
    for root, subf, files in os.walk(path):
        for fs in files:
            if fs in JS_FILES:
                minfile(os.path.join(root, fs))

def minfile(filename):
    insize = os.path.getsize(filename)
    print "Processing %s: %d ->" % (filename, insize),
    cmd = CMD % {'type': 'js', 'file': filename}
    print get_command_output(cmd)
    outsize = os.path.getsize(filename)
    print "%d [%.2f%%]" % (outsize, ((insize-outsize)*100)/insize)

if __name__ == "__main__":
    minimizejs(os.path.normpath('/workspace/cdn/media/app/vertaal/1.6.1/'))