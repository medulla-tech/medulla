# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>

import urllib.parse
import re
import io

from twisted.internet import reactor, defer
from twisted.web import client
from twisted.internet import interfaces, protocol
from zope.interface import implementer

import logging

logger = logging.getLogger()

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

    login_namename = b"medulladefault"
    login_passwordname = b"password"
    glpi_csrf_token = b"your_csrf_token_value"

    def __init__(self, conffile=None, name="glpi"):
        if not conffile:
            conffile = getConfigFile(name)
        AuthenticatorI.__init__(self, conffile, name, GlpiAuthenticatorConfig)

    def _cbIndexPage(self, response):
        self.logger.debug("GlpiAuthenticator: on index page")
        set_cookie_header = response.headers.getRawHeaders(b"set-cookie")
        if set_cookie_header:
            phpsessid = set_cookie_header[0].split(b"=")
            params = {
                "method": b"POST",
                "cookies": {phpsessid[0]: phpsessid[1]},
                "headers": {
                    b"Content-Type": b"application/x-www-form-urlencoded",
                    b"Referer": urllib.parse.urljoin(
                        self.config.baseurl, self.config.loginpage
                    ),
                },
                "postdata": urllib.parse.urlencode(
                    {
                        self.login_namename: self.user,
                        self.login_passwordname: self.password,
                        b"_glpi_csrf_token": self.glpi_csrf_token,
                    }
                ).encode("utf-8"),
            }
            return params
        else:
            # Gérer le cas où l'en-tête "set-cookie" est manquant
            # Peut-être qu'il y a une autre logique à appliquer ici, selon vos besoins

            params = {
                "postdata": urllib.parse.urlencode(
                    {
                        "login": self.user,
                        "password": (
                            self.password.decode("utf-8")
                            if isinstance(self.password, bytes)
                            else self.password
                        ),
                    }
                ).encode("utf-8")
            }

            return params

    def _cbLoginPost(self, params):
        self.logger.debug("GlpiAuthenticator: posting on login page")
        d = self.agent.request(
            b"POST",
            urllib.parse.urljoin(
                self.config.baseurl.encode("utf-8"),
                self.config.loginpost.encode("utf-8"),
            ),
            headers=client.Headers({b"User-Agent": [b"Twisted Client"]}),
            bodyProducer=client.FileBodyProducer(io.BytesIO(params["postdata"])),
        )
        d.addCallback(self._cbCheckOutput)
        return d

    def _cbCheckOutput(self, response):
        deferred = defer.Deferred()
        response.deliverBody(GlpiAuthenticator._ResponseReader(deferred))
        return deferred

    class _ResponseReader(protocol.Protocol):
        def __init__(self, deferred):
            self.deferred = deferred
            self.data = b""

        def dataReceived(self, chunk):
            self.data += chunk

        def connectionLost(self, reason):
            self.deferred.callback(self.data)

    def _cbReadResponseBody(self, body):
        content = body.read()
        return re.search(self.config.match, content.decode("utf-8")) is not None

    def authenticate(self, user, password):
        """
        Return a deferred object resulting to True or False
        """
        if not self.config.doauth:
            self.logger.debug(
                "GlpiAuthenticator: do not authenticate user %s (doauth = False)" % user
            )
            return defer.succeed(True)

        self.user = user
        self.password = password
        self.agent = client.Agent(reactor)
        d = self.agent.request(
            b"GET",
            urllib.parse.urljoin(self.config.baseurl, self.config.loginpage).encode(
                "utf-8"
            ),
            headers=client.Headers({b"User-Agent": [b"Twisted Client"]}),
        )
        d.addCallback(self._cbIndexPage)
        d.addCallback(self._cbLoginPost)
        return d

    def validate(self):
        return True


@implementer(interfaces.IPushProducer)
class StringProducer:
    def __init__(self, body):
        self.body = body
        self.paused = False

    def pauseProducing(self):
        self.paused = True

    def resumeProducing(self):
        if self.paused:
            self.paused = False
            self.consumer.write(self.body)

    def stopProducing(self):
        pass

    def startProducing(self, consumer):
        self.consumer = consumer
        self.consumer.write(self.body)
