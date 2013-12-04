# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2013 Mandriva, http://www.mandriva.com
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
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
