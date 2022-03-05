# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Pulse Pull Client.
#
# Pulse Pull client is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse Pull Client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
"""
A simple HTTP client for communicating with the DLP webservice
"""

import json
from . import http.cookiejar
import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
import logging
import contextlib


logger = logging.getLogger(__name__)


class HTTPErrorHandler(urllib.request.HTTPDefaultErrorHandler):
    def http_error_default(self, req, res, code, msg, hdrs):
        return res


class CookieSessionExpired(Exception):
    pass


class HTTPClient(object):
    def __init__(self, base_url, identity=None):
        self.cookie_jar = http.cookiejar.CookieJar()
        handlers = [urllib.request.HTTPCookieProcessor(self.cookie_jar)]
        if self.config.Proxy.http:
            proxy_handler = urllib.request.ProxyHandler(
                {"http": self.config.Proxy.http}
            )
        else:
            proxy_handler = urllib.request.ProxyHandler()
        handlers.append(proxy_handler)
        handlers.append(HTTPErrorHandler)
        self.opener = urllib.request.build_opener(*handlers)

        if identity:
            self.opener.addheaders = [("User-agent", identity)]
        urllib.request.install_opener(self.opener)
        self.base_url = base_url
        if not self.base_url.endswith("/"):
            self.base_url += "/"

    def get(self, url, headers={}):
        """HTTP GET
        url should be a string containing a valid URL.
        headers should be a dictionary
        """
        # Mutable dict headers used as default argument to a method or function
        url = self.base_url + url
        request = urllib.request.Request(url, headers=headers)
        return self.execute_request(request)

    def post(self, url, data=None, headers={}):
        """HTTP POST

        url should be a string containing a valid URL.
        data should be a url-encodable dictionary
        headers should be a dictionary
        """
        # Mutable dict headers used as default argument to a method or function
        url = self.base_url + url
        if data is None:
            postdata = None
        else:
            postdata = urllib.parse.urlencode(data, True)
        request = urllib.request.Request(url, postdata, headers)
        return self.execute_request(request)

    def execute_request(self, request):
        with contextlib.closing(self.opener.open(request)) as response:
            response.data = response.read()
            if response.info().get("Content-Type", None) == "application/json":
                response.data = json.loads(response.data)
            # if the response is not an error, and there is no cookie set for the request
            # we may get a already expired session cookie because the client or the servier
            # time is not in sync
            if response.code < 400 and not self.cookie_jar.make_cookies(
                response, request
            ):
                raise CookieSessionExpired()
        return response
