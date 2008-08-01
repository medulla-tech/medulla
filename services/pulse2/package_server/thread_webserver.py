#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id: __init__.py 30 2008-02-08 16:40:54Z nrueff $
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os.path
import logging
import twisted
import re
import SimpleHTTPServer
from twisted.web import xmlrpc, resource, static, server
from twisted.internet import reactor

from pulse2.package_server.server import P2PSite, makeSSLContext
from pulse2.package_server.description import Description
from pulse2.package_server.common import Common
from pulse2.package_server.mirror_api import MirrorApi
from pulse2.package_server.mirror import Mirror
from pulse2.package_server.package_api_get import PackageApiGet
from pulse2.package_server.package_api_put import PackageApiPut
from pulse2.package_server.user_package_api import UserPackageApi
from pulse2.package_server.config import config_addons

"""
    Pulse2 PackageServer
"""

class MyServer(resource.Resource):
    def register(self, klass, mp):
        mp = re.compile('^/').sub('', mp)
        return self.putChild(mp, klass)

def initialize(config):
    logger = logging.getLogger()
    
    port = int(config.port)
            
    server = MyServer()
    services = []
    if len(config.mirrors) > 0:
        for mirror_params in config.mirrors:
            m_api = Mirror(mirror_params['mount_point'], mirror_params['mount_point'])
            server.register(m_api, mirror_params['mount_point'])
            services.append({'type':'mirror', 'mp':mirror_params['mount_point'], 'server':config.bind, 'port':config.port, 'proto':config.proto, 'src':mirror_params['src'], 'url':'%s://%s:%s%s'%(config.proto, config.bind, config.port, mirror_params['mount_point'])})
            server.register(static.File(mirror_params['src']), mirror_params['mount_point']+'_files')
            services.append({'type':'mirror_files', 'mp':mirror_params['mount_point']+'_files', 'server':config.bind, 'port':config.port, 'proto':config.proto, 'src':mirror_params['src']})

    if len(config.package_api_get) > 0:
        for mirror_params in config.package_api_get:
            p_api = PackageApiGet(mirror_params['mount_point'], mirror_params['mount_point'])
            server.register(p_api, mirror_params['mount_point'])
            services.append({'type':'package_api_get', 'mp':mirror_params['mount_point'], 'server':config.bind, 'port':config.port, 'proto':config.proto, 'src':mirror_params['src'], 'url':'%s://%s:%s%s'%(config.proto, config.bind, config.port, mirror_params['mount_point'])})

    if len(config.package_api_put) > 0:
        for mirror_params in config.package_api_put:
            p_api = PackageApiPut(mirror_params['mount_point'], mirror_params['mount_point'], mirror_params['tmp_input_dir'])
            server.register(p_api, mirror_params['mount_point'])
            services.append({'type':'package_api_put', 'mp':mirror_params['mount_point'], 'server':config.bind, 'port':config.port, 'proto':config.proto, 'src':mirror_params['src'], 'url':'%s://%s:%s%s'%(config.proto, config.bind, config.port, mirror_params['mount_point'])})
 
    if config.user_package_api.has_key('mount_point'):
        mirror = UserPackageApi(services, config.user_package_api['mount_point'])
        server.register(mirror, config.user_package_api['mount_point'])
        services.append({'type':'user_package_api', 'mp':config.user_package_api['mount_point'], 'server':config.bind, 'port':config.port, 'proto':config.proto})
        
    if config.mirror_api.has_key('mount_point'):
        mirror = MirrorApi(services, config.mirror_api['mount_point'], config.assign_algo)
        server.register(mirror, config.mirror_api['mount_point'])
        services.append({'type':'mirror_api', 'mp':config.mirror_api['mount_point'], 'server':config.bind, 'port':config.port, 'proto':config.proto})
    else:
        logger.warn('package server initialized without mirror api')
 
    server.register(Description(services), 'desc')
    Common().setDesc(services)
    
    try:
        if config.enablessl:
            logger.debug(config.localcert + " " + config.cacert)
            if not os.path.isfile(config.localcert):
                logger.error('can\'t read SSL key "%s"' % (config.localcert))
                return 1
            if not os.path.isfile(config.cacert):
                logger.error('can\'t read SSL certificate "%s"' % (config.cacert))
                return 1
            sslContext = makeSSLContext(config.verifypeer, config.cacert, config.localcert)
            twisted.internet.reactor.listenSSL(
                port,
                P2PSite(server),
                interface = config.bind,
                contextFactory = sslContext
                )
            logger.info('activating SSL mode')
        else:
            twisted.internet.reactor.listenTCP(
                port,
                twisted.web.server.Site(server),
                interface = config.bind
                )
    except Exception, e:
        logger.error('can\'t bind to %s:%d' % (config.bind, port))
        logger.error(e)
        return 1

    logger.info('package server listening on %s:%d' % (config.bind, port))
