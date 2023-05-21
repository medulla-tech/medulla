# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

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
PULSE_DEPRECATED
"""

import os
import stat
import base64
import logging
import traceback

import xmlrpc.client
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
            auth = f"{self.factory.user}:{self.factory.password}"
            auth = base64.b64encode(bytes(auth, "utf-8"))
            self.sendHeader(b"Authorization", b"Basic %s" % (auth,))
        try:
            # Put MMC session cookie
            if (
                b"<methodName>base.ldapAuth</methodName>"
                not in self.factory.payload
            ):
                with open(COOKIES_FILE, "r") as h:
                    self.sendHeader(b"Cookie", h.read())
        except FileNotFoundError as error_opening_cookie:
            logger.error(f"An error occured while open the file {COOKIES_FILE}.")
            logger.error("The error is \n %s" % error_opening_cookie)
        except IOError as error_ioerror:
            logger.error(f"An unkown error occured. The message is {error_ioerror}")
            logger.error("We hit the backtrace: \n %s" % traceback.format_exc())
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
            with open(COOKIES_FILE, "w+") as h:
                h.write(self._session)
            os.chmod(COOKIES_FILE, stat.S_IRUSR | stat.S_IWUSR)
            self._response = contents


class MMCQueryFactory(xmlrpc.Proxy):
    protocol = MMCQueryProtocol


class Proxy(xmlrpc.Proxy):
    queryFactory = MMCQueryFactory
