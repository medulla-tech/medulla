# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Set of classes to connect to a MMC server, and do XML-RPC requests.

Example:
import mmc.client.async

def cb(result):
    print result
    reactor.stop()

proxy = async.Proxy("https://127.0.0.1:7080/XMLRPC", "mmc", "s3cr3t")
proxy.callRemote("base.ldapAuth", "root", "passpass").addCallbacks(cb)
reactor.run()
"""

import os
import stat
from twisted.web import xmlrpc

COOKIES_FILE = '/tmp/mmc-cookies'

class MMCQueryProtocol(xmlrpc.QueryProtocol):

    def connectionMade(self):
        self.sendCommand('POST', self.factory.path)
        self.sendHeader('User-Agent', 'Twisted/XMLRPClib')
        self.sendHeader('Host', self.factory.host)
        self.sendHeader('Content-type', 'text/xml')
        self.sendHeader('Content-length', str(len(self.factory.payload)))
        if self.factory.user:
            auth = '%s:%s' % (self.factory.user, self.factory.password)
            auth = auth.encode('base64').strip()
            self.sendHeader('Authorization', 'Basic %s' % (auth,))
        try:
            # Put MMC session cookie
            if not '<methodName>base.ldapAuth</methodName>' in self.factory.payload:
                h = open(COOKIES_FILE, 'r')
                self.sendHeader('Cookie', h.read())
                h.close()
        except IOError:
            pass
        self.endHeaders()
        self.transport.write(self.factory.payload)

    def lineReceived(self, line):
        xmlrpc.QueryProtocol.lineReceived(self, line)
        if line:
            if line.startswith("Set-Cookie: "):
                self._session = line.split()[1]

    def handleResponse(self, contents):
        xmlrpc.QueryProtocol.handleResponse(self, contents)
        if '<methodName>base.ldapAuth</methodName>' in self.factory.payload:
            h = open(COOKIES_FILE, 'w+')
            h.write(self._session)
            h.close()
            os.chmod(COOKIES_FILE, stat.S_IRUSR | stat.S_IWUSR)


class MMCQueryFactory(xmlrpc._QueryFactory):

    protocol = MMCQueryProtocol


class Proxy(xmlrpc.Proxy):

    queryFactory = MMCQueryFactory
