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
Common dlp configuration for wgsi and server mode
"""

import cherrypy

default_conf = {
    'tools.sessions.on': True,
    'tools.sessions.storage_type': "ram",
    'tools.sessions.timeout': 100,
    'request.show_tracebacks': False,
    'log.screen': True,
    'log.access_file': '',
    'log.error_file': '',
    'xmlrpc.client': 'xmlrpclib.ServerProxy',
    'xmlrpc.uri': "https://username:password@localhost:8000",
    'dlp.authkey': "secret",
    'dlp.cache_dir': "/var/lib/pulse2/dlp_packages/",
    'dlp.cache_expire': 108000,
    'dlp.loglevel': "ERROR",
    'inventory.uri': 'http://localhost:9999'
}

app_config = {
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    }
}
