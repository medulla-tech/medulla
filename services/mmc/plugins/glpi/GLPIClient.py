#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Glpi rest client to interact with GLPI webservices plugin
# This program is part of python-glpi lib:
#
# https://github.com/mcphargus/python-glpi
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import logging
import xmlrpclib

class XMLRPCClient(object):
    """
    Python XMLRPC client for GLPI webservices plugin
    """
    def __init__(self, baseurl="http://localhost/glpi"):
        self.baseurl = baseurl
        self.serviceurl = self.baseurl + '/plugins/webservices/xmlrpc.php'
        self.session = None
        self.server = xmlrpclib.ServerProxy(self.serviceurl)
        self.logger = logging.getLogger()

    def connect(self, login_name=None, login_password=None):
        if not None in [login_name, login_password]:
            params = {
                'login_name':login_name,
                'login_password':login_password,
            }
            response = self.server.glpi.doLogin(params)

            if 'session' in response:
                self.session = response['session']
            else:
                raise Exception("Login incorrect or server down")
        else:
            self.logger.warn("Connected anonymously, will only be able to use non-authenticated methods")
        return True

    def __getattr__(self, attr):
        def call(module='glpi', *args, **kwargs):
            params = {}
            if self.session:
                params['session'] = self.session

            params = dict(params.items() + kwargs.items())

            called_module = getattr(self.server, module)
            return getattr(called_module, attr)(params)

        call.__name__ = attr
        call.__doc__ = call(help=True)
        return call
