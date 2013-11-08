#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
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
    Pulse2 package parser module
"""
import logging
import os
from xml.dom import minidom
from pulse2.package_server.types import Package


class PackageParser:
    def init(self, config):
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
        try:
            if os.path.exists(file):
                xml = minidom.parse(file)
            else:
                xml = minidom.parseString(file)

            # parsing routines
            self.logger = logging.getLogger()
            root = xml.getElementsByTagName('package')
            if len(root) != 1:
                raise Exception('CANTPARSE')
            root = root[0]
            pid = root.getAttribute('id')
            tmp = root.getElementsByTagName('name')[0]
            name = tmp.firstChild.wholeText.strip()
            version = root.getElementsByTagName('version')[0]
            tmp = version.getElementsByTagName('numeric')[0]
            tmp = version.getElementsByTagName('label')[0]
            if tmp.firstChild != None:
                v_txt = tmp.firstChild.wholeText.strip()
            else:
                v_txt = "0"
            tmp = root.getElementsByTagName('description')
            if len(tmp) == 1 and tmp[0].firstChild != None:
                tmp = tmp[0]
                desc = tmp.firstChild.wholeText.strip()
            else:
                desc = ""

            cmd = root.getElementsByTagName('commands')[0]
            reboot = 0
            if cmd.hasAttribute('reboot'):
                reboot = cmd.getAttribute('reboot')

            cmds = {}
            for c in ['installInit', 'preCommand', 'command', 'postCommandSuccess', 'postCommandFailure']:
                tmp = cmd.getElementsByTagName(c)
                if len(tmp) == 1 and tmp[0].firstChild != None:
                    command = tmp[0].firstChild.wholeText.strip()
                    if tmp[0].hasAttribute('name'):
                        ncmd = tmp[0].getAttribute('name')
                    else:
                        ncmd = ''
                    cmds[c] = {'command':command, 'name':ncmd}
                else:
                    cmds[c] = ''

            group = root.getElementsByTagName('group')
            query = ''
            boolcnd = ''
            if len(group) == 1 and group[0].firstChild != None:
                tmp = group[0].getElementsByTagName('query')
                if len(tmp) ==1 and tmp[0].firstChild != None:
                    query = tmp[0].firstChild.wholeText.strip()
                tmp = group[0].getElementsByTagName('bool')
                if len(tmp) ==1 and tmp[0].firstChild != None:
                    boolcnd = tmp[0].firstChild.wholeText.strip()

            p = Package()
            p.init(
                pid,
                name,
                v_txt,
                0,
                desc,
                cmds['command'],
                cmds['installInit'],
                cmds['preCommand'],
                cmds['postCommandSuccess'],
                cmds['postCommandFailure'],
                reboot,
                query,
                boolcnd
            )
        except Exception, e:
            logging.getLogger().error("parse_str failed")
            logging.getLogger().error(e)
            p = None

        return p

    def to_xml(self, package):
        """
        create XML document for the package
        """

        imp = minidom.getDOMImplementation('')
        # Create document type
        dt = imp.createDocumentType('package', '', '')
        dt.internalSubset = self.doctype()

        # Create XML document with this document type
        doc = imp.createDocument('', 'package', dt)

        docr = doc.documentElement
        pid = doc.createAttribute('id')
        pid.value = package.id
        docr.setAttributeNode(pid)

        name = doc.createElement('name')
        name.appendChild(doc.createTextNode(package.label))
        docr.appendChild(name)

        version = doc.createElement('version')
        numeric = doc.createElement('numeric')
        numeric.appendChild(doc.createTextNode(str(package.version)))
        label = doc.createElement('label')
        label.appendChild(doc.createTextNode(str(package.version)))
        version.appendChild(numeric)
        version.appendChild(label)
        docr.appendChild(version)

        description = doc.createElement('description')
        description.appendChild(doc.createTextNode(package.description))
        docr.appendChild(description)

        commands = doc.createElement('commands')
        reboot = doc.createAttribute('reboot')
        reboot.value = str(package.reboot)
        commands.setAttributeNode(reboot)

        precommand = doc.createElement('preCommand')
        precommandname = doc.createAttribute('name')
        precommandname.value = package.precmd.name
        precommand.setAttributeNode(precommandname)
        precommand.appendChild(doc.createTextNode(package.precmd.command))

        installinit = doc.createElement('installInit')
        installinitname = doc.createAttribute('name')
        installinitname.value = package.initcmd.name
        installinit.setAttributeNode(installinitname)
        installinit.appendChild(doc.createTextNode(package.initcmd.command))

        command = doc.createElement('command')
        commandname = doc.createAttribute('name')
        commandname.value = package.cmd.name
        command.setAttributeNode(commandname)
        command.appendChild(doc.createTextNode(package.cmd.command))

        postsuccess = doc.createElement('postCommandSuccess')
        postsuccessname = doc.createAttribute('name')
        postsuccessname.value = package.postcmd_ok.name
        postsuccess.setAttributeNode(postsuccessname)
        postsuccess.appendChild(doc.createTextNode(package.postcmd_ok.command))

        postfailure = doc.createElement('postCommandFailure')
        postfailurename = doc.createAttribute('name')
        postfailurename.value = package.postcmd_ko.name
        postfailure.setAttributeNode(postfailurename)
        postfailure.appendChild(doc.createTextNode(package.postcmd_ko.command))

        commands.appendChild(precommand)
        commands.appendChild(installinit)
        commands.appendChild(command)
        commands.appendChild(postsuccess)
        commands.appendChild(postfailure)

        docr.appendChild(commands)

        group = doc.createElement('group')
        query = doc.createElement('query')
        query.appendChild(doc.createTextNode(package.query))
        boolcnd = doc.createElement('bool')
        boolcnd.appendChild(doc.createTextNode(package.boolcnd))
        group.appendChild(query)
        group.appendChild(boolcnd)
        
        docr.appendChild(group)

        return doc.toprettyxml(encoding = 'utf-8')

    def doctype(self):
        return """
    <!ELEMENT package (name,version,description?,commands,files?, group?)>
    <!ATTLIST package id ID #REQUIRED>

    <!ELEMENT name (#PCDATA)>
    <!ELEMENT version (numeric,label)>
    <!ELEMENT numeric (#PCDATA)>
    <!ELEMENT label (#PCDATA)>
    <!ELEMENT description (#PCDATA)>

    <!ELEMENT commands (preCommand?,installInit?,command,postCommandSuccess?,postCommandFailure?)>
    <!ATTLIST commands reboot (0|1) "0">
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
    <!ELEMENT group (query, bool)>
    <!ELEMENT query (#PCDATA)>
    <!ELEMENT bool (#PCDATA)>
"""





