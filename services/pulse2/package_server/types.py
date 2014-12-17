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
    Pulse2 Package server types
"""

from pulse2.package_server.utilities import md5sum
import pulse2.package_server.common
import urllib
import locale

class Mirror:
    def __init__(self, protocol = None, server = None, port = None, mountpoint = None):
        self.protocol = protocol
        self.server = server
        self.port = port
        self.mountpoint = mountpoint
        self.uuid = "UUID%s"%(mountpoint)

    def toH(self):
        return { 'protocol' : self.protocol, 'server' : self.server, 'port' : str(self.port), 'mountpoint' : self.mountpoint, 'uuid' : self.uuid }

    def fromH(self, h):
        self.protocol = h['protocol']
        self.server = h['server']
        self.port = h['port']
        self.mountpoint = h['mountpoint']
        self.uuid = "UUID%s" % (self.mountpoint)

    def equal(self, a):
        if self.protocol == a.protocol and self.server == a.server and self.port == a.port and self.mountpoint == a.mountpoint:
            return True
        return False


class Command:
    def __init__(self, name = '', command = ''):
        self.name = name
        self.command = command

    def toH(self):
        return { 'name':self.name, 'command':self.command }

    def fromH(self, h):
        if type(h) == dict:
            self.name = h['name']
            self.command = h['command']
        elif type(h) == Command:
            self.name = h.name
            self.command = h.command
        elif type(h) == str:
            self.command = h
            self.name = ''

    def to_s(self):
        return self.command

    def equal(self, c):
        if self.name != c.name or self.command != c.command:
            return False
        return True

def getCommandFromH(h):
    cmd = Command()
    cmd.fromH(h)
    return cmd

class A_Packages:
    def __init__(self, a):
        self.packages = a

class Package:
    def __init__(self):
        self.files = AFiles()
        self.specifiedFiles = []

    def init(self, id, label, version, size, description, cmd, initcmd='',
             precmd='', postcmd_ok='', postcmd_ko='', reboot=0, appstream_family='', Qvendor='',
             Qsoftware='', Qversion='', boolcnd='', licenses='',
             associateinventory=0):
        self.label = label
        self.version = version
        self.size = size
        if self.size == None:
            self.size = 0
        self.description = description
        self.initcmd = getCommandFromH(initcmd)
        self.precmd = getCommandFromH(precmd)
        self.cmd = getCommandFromH(cmd)
        self.postcmd_ok = getCommandFromH(postcmd_ok)
        self.postcmd_ko = getCommandFromH(postcmd_ko)
        self.reboot = reboot
        self.appstream_family = appstream_family
        self.id = id
        self.root = ''
        self.Qvendor = Qvendor
        self.Qsoftware = Qsoftware
        self.Qversion = Qversion
        self.boolcnd = boolcnd
        self.licenses = licenses
        self.associateinventory = associateinventory

    def addFile(self, file):
        self.files.append(file)

    def setFiles(self, files):
        self.files = files

    def hasFile(self):
        return not self.files.isEmpty()

    def setRoot(self, root):
        self.root = root

    def toH(self):
        ret = {
            'label':self.label,
            'version':self.version,
            'size':self.size,
            'id':self.id,
            'description':self.description,
            'installInit':self.initcmd.toH(),
            'preCommand':self.precmd.toH(),
            'command':self.cmd.toH(),
            'postCommandSuccess':self.postcmd_ok.toH(),
            'postCommandFailure':self.postcmd_ko.toH(),
            'reboot':self.reboot,
            'appstream_family': self.appstream_family,
            'files':self.files.toH(),
            'Qvendor':self.Qvendor,
            'Qsoftware':self.Qsoftware,
            'Qversion':self.Qversion,
            'boolcnd':self.boolcnd,
            'licenses': self.licenses,
            'associateinventory': self.associateinventory
        }
        if self.root != '':
            # The package root is decoded using the current encoding to get a Python
            # unicode string, so that non-ASCII characters can later be successfully
            # written into a XML-RPC stream
            try:
                root = self.root.decode(locale.getpreferredencoding())
            except:
                root = self.root
            ret['basepath'] = root
        return ret

    def to_h(self):
        return self.toH()

    def fromH(self, h):
        self.label = h['label']
        self.version = h['version']
        self.id = h['id']
        if h.has_key('size') and h['size'] != '':
            self.size = h['size']
        else:
            self.size = "0"
        if h.has_key('description'):
            self.description = h['description']
        else:
            self.description = ''

        if h.has_key('installInit'):
            self.initcmd = getCommandFromH(h['installInit'])
        else:
            self.initcmd = Command()
        if h.has_key('preCommand'):
            self.precmd = getCommandFromH(h['preCommand'])
        else:
            self.precmd = Command()
        if h.has_key('command'):
            self.cmd = getCommandFromH(h['command'])
        else:
            self.cmd = Command()
        if h.has_key('postCommandSuccess'):
            self.postcmd_ok = getCommandFromH(h['postCommandSuccess'])
        else:
            self.postcmd_ok = Command()
        if h.has_key('postCommandFailure'):
            self.postcmd_ko = getCommandFromH(h['postCommandFailure'])
        else:
            self.postcmd_ko = Command()
        self.appstream_family = ''
        if h.has_key('appstream_family'):
            self.appstream_family = h['appstream_family']
        self.reboot = 0
        if h.has_key('reboot'):
            self.reboot = h['reboot']
        self.root = ''
        if h.has_key('basepath'):
            self.root = h['basepath']
        if h.has_key('Qvendor'):
            self.Qvendor = h['Qvendor']
        if h.has_key('Qsoftware'):
            self.Qsoftware = h['Qsoftware']
        if h.has_key('Qversion'):
            self.Qversion = h['Qversion']
        if h.has_key('boolcnd'):
            self.boolcnd = h['boolcnd']
        if h.has_key('licenses'):
            self.licenses = h['licenses']
        if h.has_key('associateinventory'):
            self.associateinventory = h['associateinventory']
        return self

    def equal(self, p):
        if self.label != p.label or self.version != p.version or self.size != p.size or self.id != p.id or not(self.initcmd.equal(p.initcmd)) or not(self.precmd.equal(p.precmd)) or not(self.cmd.equal(p.cmd)) or not(self.postcmd_ok.equal(p.postcmd_ok)) or not(self.postcmd_ko.equal(p.postcmd_ko)) or self.description != p.description:
            return False
        # TODO check files
        return True

class AFiles:
    def __init__(self):
        self.internals = []

    def append(self, elt):
        self.internals.append(elt)

    def isEmpty(self):
        return (len(self.internals) == 0)

    def toH(self):
        return map(lambda x: x.toH(), self.internals)

    def to_h(self):
        return self.toH()

    def toURI(self, mp = None):
        if mp == None:
            return map(lambda x: x.toURI(), self.internals)
        else:
            d = pulse2.package_server.common.Common().h_desc(mp)
            if d.has_key("mirror_url") and d['mirror_url'] != '':
                where = d['mirror_url']
            elif d.has_key("url") and d['url'] != '':
                where = "%s_files"%(d['url'])
            else:
                where = "%s://%s:%s%s_files" % (d['proto'], d['server'], str(d['port']), d['mp'])
            return map(lambda x: x.toURI(mp, where), self.internals)

class File:
    def __init__(self, name = None, path = '/', checksum = None, size = 0, access = None, id = None):
        if access is None: # dont modify the default value!
            access = {}
        if access.has_key('mirror'):
            self.where = access['mirror']
        else:
            if not access.has_key('proto'):
                access['proto'] = 'http'
            if not access.has_key('file_access_uri'):
                access['file_access_uri'] = '127.0.0.1'
            if not access.has_key('file_access_port'):
                access['file_access_port'] = '80'
            if not access.has_key('file_access_path'):
                access['file_access_path'] = ''
            self.where = "%s://%s:%s%s" % (access['proto'], access['file_access_uri'], str(access['file_access_port']), access['file_access_path'])
        
        self.name = name
        self.path = path
        self.checksum = checksum
        self.size = size
        if id == None:
            self.id = md5sum("%s%s" % (self.toS().replace('\\', '/'), str(self.checksum)))
        else:
            self.id = id

    def toURI(self, mp = None, where = None):
        if mp == None:
            return ("%s%s/%s" % (self.where, self.path.replace('\\', '/'), self.name)).replace(' ', '%20')
        else:
            if where == None:
                d = pulse2.package_server.common.Common().h_desc(mp)
                if d.has_key("mirror_url") and d['mirror_url'] != '':
                    where = d['mirror_url']
                elif d.has_key("mirror_mp") and d['mirror_mp'] != '':
                    where = "%s://%s:%s%s" % (d['proto'], d['server'], str(d['port']), d['mirror_mp'])
                else:
                    where = "%s://%s:%s%s_files" % (d['proto'], d['server'], str(d['port']), d['mp'])
            ret = where + urllib.quote("%s/%s" % (self.path.replace('\\', '/'), self.name))
            return (ret)

    def toS(self):
        return "%s/%s" % (self.path, self.name)

    def to_s(self):
        return self.toS()

    def toH(self):
        # The file name and path are decoded using the current encoding to get a
        # Python unicode string, so that non-ASCII characters can be later successfully
        # written into a XML-RPC stream
        try:
            name = self.name.decode(locale.getpreferredencoding())
        except:
            name = self.name
        try:
            path = self.path.decode(locale.getpreferredencoding())
        except:
            path = self.path
        return { 'name':name, 'path':path, 'id':self.id }

    def to_h(self):
        return self.toH()

class Machine:
    def __init__(self, name = None, uuid = None):
        self.name = name
        self.uuid = uuid

    def uuid(self):
        return self.uuid

    def to_h(self):
        return { 'name' : self.name, 'uuid' : self.uuid }

    def from_h(self, h):
        if h.has_key('name'):
            self.name = h['name']
        else:
            self.name = ''
        try:
            self.uuid = h['uuid']
        except Exception, e:
            raise Exception("machine must have an uuid: " + str(e))
        return self

    def equal(self, a):
        return self.name == a.name

class User:
    def __init__(self, name = None, uuid = None):
        self.name = name
        self.uuid = name

    def to_h(self):
        return { 'name' : self.name, 'uuid' : self.uuid }

    def from_h(self, h):
        if h.has_key('name'):
            self.name = h['name']
        else:
            self.name = ''
        try:
            self.uuid = h['uuid']
        except Exception, e:
            raise Exception("user must have an uuid: " + str(e))
        return self

    def equal(self, a):
        return (self.name == a.name and self.uuid == a.uuid)


