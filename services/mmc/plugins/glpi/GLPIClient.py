#!/usr/bin/env python3
#-*- coding:utf-8 -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText:2007-2014 Mandriva, http://www.mandriva.com
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Glpi rest client to interact with GLPI webservices plugin
This program is part of python-glpi lib:

https://github.com/mcphargus/python-glpi
"""
import logging
import xmlrpc.client


class XMLRPCClient(object):
    """
    Python XMLRPC client for GLPI webservices plugin
    """

    def __init__(self, baseurl="http://localhost/glpi"):
        self.baseurl = baseurl
        self.serviceurl = self.baseurl + "/plugins/webservices/xmlrpc.php"
        self.session = None
        self.server = xmlrpc.client.ServerProxy(self.serviceurl)
        self.logger = logging.getLogger()

    def connect(self, login_name=None, login_password=None):
        if not None in [login_name, login_password]:
            params = {
                "login_name": login_name,
                "login_password": login_password,
            }
            response = self.server.glpi.doLogin(params)

            if "session" in response:
                self.session = response["session"]
            else:
                raise Exception("Login incorrect or server down")
        else:
            self.logger.warn(
                "Connected anonymously, will only be able to use non-authenticated methods"
            )
        return True

    def __getattr__(self, attr):
        def call(module="glpi", *args, **kwargs):
            params = {}
            if self.session:
                params["session"] = self.session

            params = dict(list(params.items()) + list(kwargs.items()))

            called_module = getattr(self.server, module)
            return getattr(called_module, attr)(params)

        call.__name__ = attr
        call.__doc__ = call(help=True)
        return call
