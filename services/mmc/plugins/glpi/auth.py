# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
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

import urlparse
import urllib
import re

from twisted.internet import reactor, defer
from twisted.web.client import HTTPClientFactory, getPage
try:
    from twisted.web.client import _parse
    parseAvailable = True
except ImportError:
    try:
        from twisted.web.client import _URI as URI
    except ImportError:
        from twisted.web.client import URI
    parseAvailable = False

from mmc.plugins.base.auth import AuthenticatorConfig, AuthenticatorI
from mmc.support.mmctools import getConfigFile

class GlpiAuthenticatorConfig(AuthenticatorConfig):

    def readConf(self):
        AuthenticatorConfig.readConf(self)
        self.baseurl = self.get(self.section, "baseurl")
        self.doauth = self.getboolean(self.section, "doauth")

    def setDefault(self):
        AuthenticatorConfig.setDefault(self)
        self.loginpage = "index.php"
        self.loginpost = "front/login.php"
        self.match = "window.location='.*/front/central.php'|window.location='.*/front/helpdesk.public.php'"
        self.doauth = True

class GlpiAuthenticator(AuthenticatorI):
    """
    Use the HTML login page of GLPI to authenticate a user.
    This is useful to create and to provision her/his account in GLPI database.
    """

    def __init__(self, conffile = None, name = "glpi"):
        if not conffile:
            conffile = getConfigFile(name)
        AuthenticatorI.__init__(self, conffile, name, GlpiAuthenticatorConfig)

    def _cbIndexPage(self, value):
        self.logger.debug("GlpiAuthenticator: on index page")
        phpsessid = value.response_headers["set-cookie"][0].split("=")
        return {
            "method": "POST",
            "cookies": {phpsessid[0]: phpsessid[1]},
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": urlparse.urljoin(
                    self.config.baseurl, self.config.loginpage
                ),
            },
            "postdata": urllib.urlencode(
                {
                    value.login_namename: self.user,
                    value.login_passwordname: self.password,
                    "_glpi_csrf_token": value.glpi_csrf_token,
                }
            ),
        }

    def _cbLoginPost(self, params):
        self.logger.debug("GlpiAuthenticator: posting on login page")
        d = getPage(urlparse.urljoin(self.config.baseurl, self.config.loginpost), None, **params)
        d.addCallback(self._cbCheckOutput)
        return d

    def _cbCheckOutput(self, value):
        return re.search(self.config.match, value) is not None

    def authenticate(self, user, password):
        """
        Return a deferred object resulting to True or False
        """
        if not self.config.doauth:
            self.logger.debug(
                f"GlpiAuthenticator: do not authenticate user {user} (doauth = False)"
            )
            return defer.succeed(True)
        self.user = user
        self.password = password
        d = getPageWithHeader(urlparse.urljoin(self.config.baseurl, self.config.loginpage)).addCallback(self._cbIndexPage)
        d.addCallback(self._cbLoginPost)
        return d

    def validate(self):
        return True


class HTTPClientFactoryWithHeader(HTTPClientFactory):
    """
    HTTPClientFactory don't allow to get the HTTP header.
    So we subclass the page() method and modify it to get the HTTP payload
    header
    """

    # the GLPI anti-csrf token (GLPI 0.83.3+)
    glpi_csrf_token = ''

    def page(self, page):
        # grabbing the GLPI anti-csrf token (GLPI 0.83.3+) by
        # looking for such patterns :
        # <input type='hidden' name='_glpi_csrf_token' value='82d37af7f30d76f2238d49c28167654f'>
        m = re.search('input type="hidden" name="_glpi_csrf_token" value="([0-9a-z]{32})">', page)
        if m is not None:
            self.glpi_csrf_token = m[1]

        m = re.search('input type="password" name="([0-9a-z]{19})" id="login_password"', page)
        if m is not None:
            self.login_passwordname = m[1]

        m = re.search('input type="text" name="([0-9a-z]{19})" id="login_name"', page)
        if m is not None:
            self.login_namename = m[1]

        if self.waiting:
            self.waiting = 0
            self.deferred.callback(self)


def getPageWithHeader(url, contextFactory=None, *args, **kwargs):
    """
    Same as twisted.web.client.getPage, but we keep the HTTP header in the
    result thanks to the HTTPClientFactoryWithHeader class
    """
    if parseAvailable:
        scheme, host, port, path = _parse(url)
    else:
        uri = URI.fromBytes(url)
        scheme = uri.scheme
        host = uri.host
        port = uri.port

    factory = HTTPClientFactoryWithHeader(url, *args, **kwargs)
    d = factory.deferred

    if scheme == 'https':
        from twisted.internet import ssl
        if contextFactory is None:
            contextFactory = ssl.ClientContextFactory()
        reactor.connectSSL(host, port, factory, contextFactory)
    else:
        reactor.connectTCP(host, port, factory)
    return d
