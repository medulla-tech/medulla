#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id: __init__.py 30 2008-02-08 16:40:54Z nrueff $
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
    Pulse2 package parser module
"""
import logging
from xml.dom import minidom
from pulse2.package_server.types import Package

class PackageParser(Singleton):
    def __init__(self, config):
        self.logger = logging.getLogger()
        if config.parser == None or config.parser == 'XML':
            self.parser = PackageParserXML()
        else:
            self.logger.error("don't know how to parse this kind of package configuration %s" % (config.parser))
            raise Exception("UKNPKGCNF")

    def parse(self, file):
        if type(file) == str:
            return self.parser.parse_str(file)
        else:
            raise Exception("UKNPARSEMETHOD")

    def concat(self, package):
        return self.parser.to_xml(package)

class PackageParserXML:
    def parse_str(self, file):
        xml = None
        if os.path.exist(file):
            xml = minidom.parse(file)
        else: 
            xml = minidom.parseString(file)
                
        # parsing routines
        root = xml.firstChild
        pid = root.getAttribute('id')
        tmp = root.getElementsByTagName('name')[0]
        name = tmp.firstChild.wholeText
        version = root.getElementsByTagName('version')[0]
        tmp = version.getElementsByTagName('numeric')[0]
        numeric = tmp.firstChild.wholeText
        tmp = version.getElementsByTagName('label')[0]
        label = tmp.firstChild.wholeText
        tmp = root.getElementsByTagName('description')[0]
        desc = tmp.firstChild.wholeText

        cmd = root.getElementsByTagName('commands')[0]
        tmp = cmd.getElementsByTagName('preCommand')[0]
        pre = tmp.firstChild.wholeText
        npre = tmp.getAttribute('name')
        
        tmp = cmd.getElementsByTagName('installInit')[0]
        init = tmp.firstChild.wholeText
        ninit = tmp.getAttribute('name')

        tmp = cmd.getElementsByTagName('command')[0]
        cmd = tmp.firstChild.wholeText
        ncmd = tmp.getAttribute('name')

        tmp = cmd.getElementsByTagName('postCommandSuccess')[0]
        cmd = tmp.firstChild.wholeText
        ncmd = tmp.getAttribute('name')

        tmp = cmd.getElementsByTagName('postCommandFailure')[0]
        postko = tmp.firstChild.wholeText
        npostko = tmp.getAttribute('name')

        p = Package().init(
            pid,
            name,
            v_txt,
            0,
            desc,
            {'command':cmd, 'name':ncmd},
            {'command':init, 'name':ninit},
            {'command':pre, 'name':npre},
            {'command':postok, 'name':npostok},
            {'command':postko, 'name':npostko}
        )

        # TODO load files :
        #root.each_element('//files/file') do |file_node|
        #    p.specifiedFiles << {
        #        'id'=>file_node.attributes['fid'],
        #        'checksum'=>file_node.attributes['md5sum'],
        #        'size'=>file_node.attributes['size'],
        #        'filename'=>file_node.elements['./text()'].to_s
        #    }
        #end
        return p

    def to_xml(self, package):
        str = """
<package id="%s">
    <name>%s</name>
    <version>
        <numeric>%s</numeric>
        <label>%s</label>
    </version>
    <description>%s</description>
    <commands>
        <preCommand name"%s">%s</preCommand>
        <installInit name"%s">%s</installInit>
        <command name"%s">%s</command>
        <postCommandSuccess name"%s">%s</postCommandSuccess>
        <postCommandFailure name"%s">%s</postCommandFailure>
    </commands>
</package>
        """ % (package.id, package.label, package.version, package.version, package.description, package.precmd.name, package.precmd.version, package.initcmd.name, package.initcmd.command, package.cmd.name, package.cmd.command, package.postcmd_ok.name, package.postcmd_ok.command, package.postcmd_ko.name, package.postcmd_ko.command)

        # TODO add files informations
        #if not package.files.nil? and package.files.size > 0 then
        #    files = root.add_element('files')
        #    package.files.each do |f|
        #        file = files.add_element('file')
        #        file.text = f.path + '/' + f.name
        #        # TODO add size, md5sum, id...
        #    end
        #end

        return "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n%s%s" % (self.doctype(), str)

    def doctype(self):
        return """
<!DOCTYPE package [
    <!ELEMENT package (name,version,description?,commands,files?)>
    <!ATTLIST package id ID #REQUIRED>

    <!ELEMENT name (#PCDATA)>
    <!ELEMENT version (numeric,label)>
    <!ELEMENT numeric (#PCDATA)>
    <!ELEMENT label (#PCDATA)>
    <!ELEMENT description (#PCDATA)>

    <!ELEMENT commands (preCommand?,installInit?,command,postCommandSuccess?,postCommandFailure?)>
    <!ELEMENT preCommand (#PCDATA)>
    <!ATTLIST preCommand name CDATA "">
    <!ELEMENT installInit (#PCDATA)>
    <!ATTLIST installInit name CDATA "">
    <!ELEMENT command (#PCDATA)>
    <!ATTLIST command name CDATA "">
    <!ELEMENT postCommandSuccess (#PCDATA)>
    <!ATTLIST postCommandSuccess name CDATA "">
    <!ELEMENT postCommandFailure (#PCDATA)>
    <!ATTLIST postCommandFailure name CDATA "">

    <!ELEMENT files (file*)>
    <!ELEMENT file (#PCDATA)>
    <!ATTLIST file fid ID #IMPLIED>
    <!ATTLIST file md5sum CDATA "">
    <!ATTLIST file size CDATA "">
]>
"""





