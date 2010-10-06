# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
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

"""
Contains main method to parse OCS Inventory XML string, and to map all XML
data to a Python dict.
"""

import logging

from xml.dom.minidom import parse, parseString
from xml.parsers import expat
from xml.dom.expatbuilder import ExpatBuilderNS

from pulse2.utils import Singleton


class EncodingSafeParser(ExpatBuilderNS):

    """
    Class that returns an Expat parser which parsing encoding option can be
    enforced.
    """

    def setEncoding(self, encoding):
        """
        Allow to force parser encoding
        """
        self.encoding = encoding

    def createParser(self):
        """Create a new parser object."""
        return expat.ParserCreate(self.encoding)


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

    def parseSafe(self, xmlstring):
        """
        Try to parse the file with other encodings
        """
        xml = None
        for encoding in ['ISO-8859-1', 'UTF-8']:
            self.logger.info('Trying to parse with enforced %s encoding'
                             % encoding)
            try:
                builder = EncodingSafeParser()
                builder.setEncoding(encoding)
                xml = builder.parseString(xmlstring)
                self.logger.info('String successfully parsed')
                # Exit for loop if success
                break
            except expat.ExpatError, e:
                self.logger.error('Parsing failed')
                if expat.errors.XML_ERROR_INVALID_TOKEN in str(e):
                    pass
                else:
                    # Unhandled error, just re-raise it
                    raise e
        if xml:
            return xml
        else:
            raise Exception("Can't parse inventory XML string")

    def parse(self, xmltext):
        """
        Parse the given XML string which is the content of a OCS inventory.
        """
        self.logger = logging.getLogger()
        xml = None
        try:
            xml = parseString(xmltext)
        except expat.ExpatError, e:
            self.logger.error("Can't parse inventory XML string")
            if expat.errors.XML_ERROR_INVALID_TOKEN in str(e):
                self.logger.error('The XML string may use a wrong encoding')
            else:
                # Unhandled error, just re-raise it
                raise e

        if not xml:
            # Let's try another encoding
            xml = self.parseSafe(xmltext)

        inventory = {}
        for tablename in self.tables:
            in_network = tablename == u'NETWORKS'
            try:
                dbtablename = self.tables[tablename][0]
                inventory[dbtablename] = []
                for tag in xml.getElementsByTagName(tablename):
                    entry = {}
                    if in_network:
                        # Skip lo interface and network device with a 127.x.x.x
                        # address.
                        try:
                            netif = tag.getElementsByTagName('DESCRIPTION')[0].childNodes[0].nodeValue
                        except:
                            netif = ''
                        try:
                            ip = tag.getElementsByTagName('IPADDRESS')[0].childNodes[0].nodeValue
                        except:
                            ip = ''
                        if netif == 'lo' or ip.startswith('127.'):
                            self.logger.debug('Skipping computer local interface from inventory')
                            continue
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

