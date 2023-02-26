# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
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
