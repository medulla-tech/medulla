# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com
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

Example:
import logging
from mmc.client import sync

log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

# use HTTPS Transport
proxy = sync.Proxy('https://mmc:s3cr3t@127.0.0.1:7080')

proxy.base.ldapAuth('root', 'secret')
print 'Version:', proxy.base.getVersion()
print 'APIVersion:', proxy.base.getApiVersion()
print 'Revision:', proxy.base.getRevision()
"""
import os
import stat
import logging

import xmlrpclib
import httplib
from urlparse import urlparse
from base64 import encodestring
from cookielib import LWPCookieJar, LoadError
from urllib2 import Request as CookieRequest

log = logging.getLogger()

COOKIES_FILE = '/tmp/mmc-cookies-sync'


class CookieResponse:
    """
    Adapter for the LWPCookieJar.extract_cookies
    """
    def __init__(self, headers):
        self.headers = headers

    def info(self):
        return self.headers


class MMCBaseTransport(object):
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
        self.accept_gzip_encoding = False
        # UGLY HACK ALERT. If we're running on Python 2.6 or earlier,
        # self.make_connection() needs to return an HTTP; newer versions
        # expect an HTTPConnection. Our strategy is to guess which is
        # running, and override self.make_connection for older versions.
        # That check and override happens here.
        if self._connection_requires_compat():
            self.make_connection = self._make_connection_compat

    def _connection_requires_compat(self):
        # UGLY HACK ALERT. Python 2.7 xmlrpclib caches connection objects in
        # self._connection (and sets self._connection in __init__). Python
        # 2.6 and earlier has no such cache. Thus, if self._connection
        # exists, we're running the newer-style, and if it doesn't then
        # we're running older-style and thus need compatibility mode.
        try:
            self._connection
            return False
        except AttributeError:
            return True

    def _make_connection_compat(self, host):
        # This method runs as make_connection under Python 2.6 and older.
        # __init__ detects which version we need and pastes this method
        # directly into self.make_connection if necessary.
        # Returns an HTTPSConnection like Python 2.7 does.
        host, self._extra_headers, x509 = self.get_host_info(host)
        return httplib.HTTPSConnection(host)

    def send_basic_auth(self, connection):
        """ Include HTTPS Basic Authentication data in a header
        """
        auth = encodestring("%s:%s" % self.credentials).strip()
        auth = 'Basic %s' %(auth,)
        connection.putheader('Authorization', auth)

    def send_cookie_auth(self, connection):
        """ Include Cookie Authentication data in a header
        """
        try:
            cj = LWPCookieJar()
            cj.load(COOKIES_FILE, ignore_discard=True, ignore_expires=True)

            for cookie in cj:
                connection.putheader('Cookie', '%s=%s' % (cookie.name, cookie.value))
            return True
        except LoadError :
            # mmc-cookies file is sometimes on bad format 
            # (probably caused by interrupted twisted sessions)
            log.warn("mmc-cookies: invalid LWP format file, resending the credentials")
            return False

    ## override the send_host hook to also send authentication info
    def send_host(self, connection, host):
        """
        This method override the send_host method of SafeTransport to send
        authentication and cookie info.
        """
        super(MMCBaseTransport, self).send_host(connection, host)
        if os.path.exists(COOKIES_FILE):
            if not self.send_cookie_auth(connection):
                self.send_basic_auth(connection) 
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

        r = h.getresponse()
        errcode = r.status
        errmsg = r.reason
        headers = r.msg

        # Creati g cookie jar
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

        return self.parse_response(r)

    # Backported from python 2.7
    def parse_response(self, response):
        # read response data from httpresponse, and parse it

        # Check for new http response object, else it is a file object
        stream = response

        p, u = self.getparser()

        while 1:
            data = stream.read(1024)
            if not data:
                break
            if self.verbose:
                print "body:", repr(data)
            p.feed(data)

        if stream is not response:
            stream.close()
        p.close()

        return u.close()


class MMCTransport(MMCBaseTransport, xmlrpclib.Transport):
    pass


class MMCSafeTransport(MMCBaseTransport, xmlrpclib.SafeTransport):
    pass


class Proxy(xmlrpclib.ServerProxy, object):
    """ This subclass ServerProxy to handle login and specific MMC
    cookies mechanism.
    Can authenticate automatically if username and passwd are provided.
    If MMC server return Fault 8003, we identify with base.ldapAuth method.
    """

    available_transports = {'http' : MMCTransport, 'https' : MMCSafeTransport}

    def __init__(self, uri, username=None, passwd=None, verbose=False):
        url = urlparse(uri)
        if url.scheme not in self.available_transports:
            raise IOError, "unsupported XML-RPC protocol"
        mmcTransport = self.available_transports[url.scheme](url.username, url.password)
        xmlrpclib.ServerProxy.__init__(self, uri, transport=mmcTransport)
        self.username = username
        self.passwd = passwd
        self.authenticating = False
