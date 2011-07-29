# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
#
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
MMC Synchronous Client.

MMC use a modify XMLRPC implementation which use cookies and authentification.
This module provides a function called MMCProxy that returned a xmlrpc.Server
object, which use a modified Transport (called here MMCSafeTransport).

Cookies are stored as a LWPCookieJar in "/tmp/mmc-cookies".
"""
import os
import stat
import logging

import xmlrpclib
from urlparse import urlparse, urlunparse
from base64 import encodestring
from cookielib import LWPCookieJar
from urllib2 import Request as CookieRequest

log = logging.getLogger()

COOKIES_FILE = '/tmp/mmc-cookies'

class MMCProxy(xmlrpclib.ServerProxy, object):
    """ This subclass ServerProxy to handle login and specific MMC
    cookies mechanism.
    Can authenticate automatically if username and passwd are provided.
    If MMC server return Fault 8003, we identify with base.ldapAuth method.
    """
    def __init__(self, uri, username=None, passwd=None, verbose=False):
        url = urlparse(uri)
        mmcTransport = MMCSafeTransport(url.username, url.password)
        xmlrpclib.ServerProxy.__init__(self, uri, transport=mmcTransport)
        self.username = username
        self.passwd = passwd
        self.authenticating = False

class CookieResponse:
    """
    Adapter for the LWPCookieJar.extract_cookies
    """
    def __init__(self, headers):
        self.headers = headers

    def info(self):
        return self.headers

class MMCSafeTransport(xmlrpclib.SafeTransport):
    """
    Standard synchronous Transport for the MMC agent.
    MMC agent provides a slightly modified XMLRPC interface.
    Each xmlrpc request has to contains a modified header containing a
    valid session ID and authentication information.
    """
    user_agent = 'AdminProxy'

    def __init__(self, username, passwd, use_datetime=0):
        """ This method returns an XMLRPC client which supports
        basic authentication through cookies.
        """
        self.credentials = (username, passwd)
        # See xmlrpc.Transport Class
        self._use_datetime = use_datetime

    def send_basic_auth(self, connection):
        """ Include HTTPS Basic Authentication data in a header
        """
        auth = encodestring("%s:%s" % self.credentials).strip()
        auth = 'Basic %s' %(auth,)
        connection.putheader('Authorization', auth)

    def send_cookie_auth(self, connection):
        """ Include Cookie Authentication data in a header
        """
        cj = LWPCookieJar()
        cj.load(COOKIES_FILE, ignore_discard=True, ignore_expires=True)

        for cookie in cj:
            connection.putheader('Cookie', '%s=%s' % (cookie.name, cookie.value))

    ## override the send_host hook to also send authentication info
    def send_host(self, connection, host):
        """
        This method override the send_host method of SafeTransport to send
        authentication and cookie info.
        """
        xmlrpclib.SafeTransport.send_host(self, connection, host)
        if os.path.exists(COOKIES_FILE):
            self.send_cookie_auth(connection)
        elif self.credentials != ():
            self.send_basic_auth(connection)

    def request(self, host, handler, request_body, verbose=0):
        # issue XML-RPC request
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        self.send_request(h, handler, request_body)
        self.send_host(h, host)
        self.send_user_agent(h)

        self.send_content(h, request_body)

        errcode, errmsg, headers = h.getreply()
        # Creating cookie jar
        cresponse = CookieResponse(headers)
        crequest = CookieRequest('https://' + host + '/')
        if '<methodName>base.ldapAuth</methodName>' in request_body:
            cj = LWPCookieJar()
            cj.extract_cookies(cresponse, crequest)
            if len(cj):
                cj.save(COOKIES_FILE, ignore_discard=True, ignore_expires=True)
                os.chmod(COOKIES_FILE, stat.S_IRUSR | stat.S_IWUSR)

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        self.verbose = verbose

        try:
            sock = h._conn.sock
        except AttributeError:
            sock = None

        return self._parse_response(h.getfile(), sock)
