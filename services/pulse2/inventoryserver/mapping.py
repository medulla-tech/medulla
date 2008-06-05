from mmc.support.mmctools import Singleton
from xml.dom.minidom import parse, parseString
import logging

class OcsMapping(Singleton):
    def initialize(self, xmlmapping):
        self.doc = parse(xmlmapping)
        self.tables = {}
        self.nomenclatures = {}

        for table in self.doc.documentElement.getElementsByTagName("MappedObject"):
            xmlname = table.getAttribute('name')
            xmlclass = table.getAttribute('class')
            self.tables[xmlname] = [xmlclass, {}]
            for field in table.getElementsByTagName('MappedField'):
                xmlfrom = field.getAttribute('from')
                xmlto = field.getAttribute('to')
                self.tables[xmlname][1][xmlfrom] = xmlto
                if field.hasAttribute('type') and field.getAttribute('type') == 'nomenclature':
                    self.tables[xmlname][1][xmlfrom] = ('nom%s%s'%(xmlclass, xmlto), xmlto)
                    if not self.nomenclatures.has_key(xmlclass):
                        self.nomenclatures[xmlclass] = {}
                    self.nomenclatures[xmlclass][xmlto] = True

    def parse(self, xmltext):
        inventory = {}
        xml = parseString(xmltext)
        for tablename in self.tables:
            try:
                dbtablename = self.tables[tablename][0]
                inventory[dbtablename] = []
                for tag in xml.getElementsByTagName(tablename):
                    entry = {}
                    for fieldname in self.tables[tablename][1]:
                        try:
                            field = tag.getElementsByTagName(fieldname)[0]
                            dbfieldname = self.tables[tablename][1][fieldname]
                            entry[dbfieldname] = field.childNodes[0].nodeValue
                        except IndexError:
                            pass
                    inventory[dbtablename].append(entry)
            except IndexError:
                pass

        return inventory

