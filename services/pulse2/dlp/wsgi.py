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
The dlp wsgi application
"""

import cherrypy

from pulse2.dlp.api.v1 import rootV1
from pulse2.dlp.config import default_conf, app_config


def application(environ, start_response):
    cherrypy.config.update(default_conf)
    cherrypy.config.update({'environment': 'embedded'})

    if 'configuration' in environ:
        cherrypy.config.update(environ['configuration'])

    cherrypy.tree.mount(rootV1, cherrypy.config.get('virtual_root', '').rstrip('/') + '/api/v1', app_config)

    return cherrypy.tree(environ, start_response)
