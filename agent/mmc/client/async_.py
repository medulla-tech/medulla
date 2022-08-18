# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
# (c) 2017-2022 Siveo, http://www.siveo.net/
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
Set of classes to connect to a MMC server, and do XML-RPC requests.

Example:
import mmc.client.async_

def cb(result):
    print result
    reactor.stop()

proxy = async_.Proxy("https://127.0.0.1:7080/XMLRPC", "mmc", "s3cr3t")
proxy.callRemote("base.ldapAuth", "root", "passpass").addCallbacks(cb)
reactor.run()
"""

import os
import stat
import base64
import logging
import traceback

from twisted.web import xmlrpc

logger = logging.getLogger()

COOKIES_FILE = "/tmp/mmc-cookies"


class MMCQueryProtocol(xmlrpc.QueryProtocol):
    def connectionMade(self):
        self._response = None
        self.sendCommand(b"POST", bytes(self.factory.path))
        self.sendHeader(b"User-Agent", b"Twisted/XMLRPClib")
        self.sendHeader(b"Host", bytes(self.factory.host))
        self.sendHeader(b"Content-type", b"text/xml")
        self.sendHeader(b"Content-length", bytes(len(self.factory.payload)))
        if self.factory.user:
            auth = "%s:%s" % (self.factory.user, self.factory.password)
            auth = base64.b64encode(bytes(auth, 'utf-8'))
            self.sendHeader(b"Authorization", b"Basic %s" % (auth,))
        try:
            # Put MMC session cookie
            if not b"<methodName>base.ldapAuth</methodName>" in self.factory.payload:
                h = open(COOKIES_FILE, "r")
                self.sendHeader(b"Cookie", h.read())
                h.close()
        except FileNotFoundError as error_opening_cookie:
            logger.error("An error occured while open the file %s." %  COOKIES_FILE)
            logger.error("The error is \n %s" % error_opening_cookie)
        except IOError as error_ioerror:
            logger.error("An unkown error occured. The message is %s" % error_ioerror)
            logger.error("We hit the backtrace: \n %s" % traceback.format_exc())
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
        if "<methodName>base.ldapAuth</methodName>" in self.factory.payload:
            h = open(COOKIES_FILE, "w+")
            h.write(self._session)
            h.close()
            os.chmod(COOKIES_FILE, stat.S_IRUSR | stat.S_IWUSR)
            self._response = contents


class MMCQueryFactory(xmlrpc._QueryFactory):

    protocol = MMCQueryProtocol


class Proxy(xmlrpc.Proxy):

    queryFactory = MMCQueryFactory
