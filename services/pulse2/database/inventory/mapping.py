# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from pulse2.utils import Singleton
from xml.dom.minidom import parse, parseString

class OcsMapping(Singleton):
    def initialize(self, xmlmapping):
        self.doc = parse(xmlmapping)
        self.tables = {}
        self.nomenclatures = {}

        for table in self.doc.documentElement.getElementsByTagName("MappedObject"):
            xmlname = table.getAttribute('name')
            xmlclass = table.getAttribute('class')
            if xmlclass == 'Null':
                continue
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

