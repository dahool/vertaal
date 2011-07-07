#from pylisa import tbx
from translate.storage import tbx

#
'''
class VertaalTbxFile:
    
    def __init__(self):
        self.tbxfile = tbx.tbxfile()
        
    def __str__(self):
        return self.tbxfile.prettyxml()
        
    def parse_glossary(self, list):
        for elem in list:
            unit = tbx.tbxunit(elem.word, target_lang=elem.language.code)
            translation = elem.translation.split(',')
            for word in translation:
                unit.add_term(word)
            if elem.comment:
                unit.add_note(elem.comment)
            self.tbxfile.add_unit(unit)
'''

class VertaalTbxFile(tbx.tbxfile):
    XMLskeleton = '''<?xml version="1.0"?> 
        <!DOCTYPE martif PUBLIC "ISO 12200:1999A//DTD MARTIF core (DXFcdV04)//EN" "TBXcdv04.dtd"> 
        <martif type="TBX"> 
        <martifHeader> 
        <fileDesc> 
        <sourceDesc><p>Vertaal</p></sourceDesc> 
        </fileDesc> 
        </martifHeader> 
        <text><body></body></text> 
        </martif>'''

    def parse_glossary(self, list):
        for elem in list:
            term = tbx.tbxunit(elem.word)
            #translation = elem.translation.split(',')
            #for word in translation:
                #term.settarget(word, lang=elem.language.code)
            term.settarget(elem.translation, lang=elem.language.code)
            if elem.comment:
                term.addnote(elem.comment)
            self.addunit(term)
