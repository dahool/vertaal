# pylisa
# Copyright (C) 2010 Sergio Gabriel Teves
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import elementtree.ElementTree as ET
from cStringIO import StringIO
from xml.dom.minidom import parseString

class tbxunit(object):

    def __init__(self, term, source_lang='en', target_lang='xx', descript=None):
        self.element = ET.Element('termEntry')
        if descript:
            ET.SubElement(self.element,'descrip',{'type': 'definition'}).text(descript)
        langset = ET.SubElement(self.element,'langSet',{'xml:lang': source_lang})
        ET.SubElement(ET.SubElement(langset,'tig'),
                      'term').text = term
        self.langset = ET.SubElement(self.element,'langSet',{'xml:lang': target_lang})

    def add_note(self, note):
        ET.SubElement(self.langset,'note').text=note

    def add_term(self, term):
        ET.SubElement(ET.SubElement(self.langset,'tig'),
                      'term').text = term
            
class tbxfile(object):
    sourceLanguage = 'en'
    sourceDesc = 'django-lisa TBX File'
    units = []
    
    def __str__(self):
        root = ET.Element('martif',{'type':'TBX',
                                    'xml:lang': self.sourceLanguage})
        martifHeader = ET.SubElement(root,'martifHeader')
        fileDesc = ET.SubElement(martifHeader,'fileDesc')
        sourceDesc = ET.SubElement(fileDesc,'sourceDesc')
        sourceDescP = ET.SubElement(sourceDesc,'p')
        sourceDescP.text = self.sourceDesc

        encoding = ET.SubElement(martifHeader,'encodingDesc')
        encodingP = ET.SubElement(encoding,'p',{'type': 'XCSURI'})
        text = ET.SubElement(root,"text")
        body = ET.SubElement(text,"body")

        eid = 1
        for unit in self.units:
            unit.element.set("id","term-entry-%d" % eid)
            body.append(unit.element)
            eid+=1
        xml = ET.ElementTree(root)
        f = StringIO()
        #xml.write(f,encoding='utf-8')
        xml.write(f)
        f.reset()
        return f.read()

    def add_unit(self, unit):
        self.units.append(unit)
        
    def prettyxml(self):
        return parseString(str(self)).toprettyxml('')
