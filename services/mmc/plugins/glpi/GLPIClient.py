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

import urllib, urllib2
import json
import logging

class RESTClient(object):
    """
    Python client for GLPI webservices plugin
    """
    def __init__(self, baseurl="http://localhost/glpi"):
        self.baseurl = baseurl
        self.resturl = self.baseurl + '/plugins/webservices/rest.php?'
        self.session = None
        self.logger = logging.getLogger()

    def connect(self, login_name=None, login_password=None):
        """
        Connect to a running GLPI instance with webservices
        plugin enabled.

        Returns True if connection was successful.

        @param login_name: your GLPI username
        @type login_name: string
        @param login_password: your GLPI password
        @type login_password: string
        """

        if not None in [login_name, login_password]:
            params = {
                'method':'glpi.doLogin',
                'login_name': login_name,
                'login_password': login_password,
            }
            response = urllib2.urlopen(self.resturl + urllib.urlencode(params))
            result = json.loads(response.read())
            if 'session' in result:
                self.session = result['session']
            else:
                raise Exception("Login incorrect or server down")
        else:
            self.logger.warn("Connected anonymously, will only be able to use non-authenticated methods")
        return True

    def __getattr__(self, attr):
        def treatFields(params):
            fields = params.pop('fields', [])
            if attr == 'deleteObjects':
                for glpi_type in fields:
                    for key, value in fields[glpi_type].items():
                        params['fields[%s][%s]' % (glpi_type, key)] = value
            elif attr == 'updateObjects':
                for glpi_type in fields:
                    for elem in fields[glpi_type]:
                        elem_id = elem['id']
                        for key, value in elem.items():
                            params['fields[%s][%s][%s]' % (glpi_type, elem_id, key)] = value
            return params

        def call(module='glpi', *args, **kwargs):
            params = {'method': '.'.join([module, attr])}
            if self.session:
                params['session'] = self.session

            params = dict(params.items() + kwargs.items())

            if 'fields' in params:
                params = treatFields(params)

            response = urllib2.urlopen(self.resturl + urllib.urlencode(params))
            return json.loads(response.read())
        return call
