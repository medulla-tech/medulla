# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Cherrypy tools for the dlp application
"""

import cherrypy
import importlib


HOSTNAME_KEY = '_hostname'
MAC_KEY = '_mac_addresses'
UUID_KEY = '_uuid'
COMMANDS_KEY = '_commands'


def is_authorized():
    """
    Authorize the request only if HOSTNAME_KEY is set.
    """
    if not cherrypy.session.get(HOSTNAME_KEY):
        raise cherrypy.HTTPError(403, "You are not allowed to access this resource")
cherrypy.tools.is_authorized = cherrypy.Tool('before_handler', is_authorized, priority=60)


def xmlrpc_client():
    """
    Provide a xmlrpc client to the scheduler in the current request.
    """
    mod_name, class_name = cherrypy.config.get('xmlrpc.client').rsplit('.', 1)
    module = importlib.import_module(mod_name)
    cherrypy.request.xmlrpc_client = getattr(module, class_name)(cherrypy.config.get('xmlrpc.uri'),
                                                                 allow_none=True)
cherrypy.tools.xmlrpc_client = cherrypy.Tool('before_handler', xmlrpc_client, priority=60)
