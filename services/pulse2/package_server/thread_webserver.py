# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Pulse 2 Package Server.
Registers all XML-RPC resources attached to the XML-RPC server.
"""

import logging
import twisted
import re
import os
from twisted.web import resource, static
from twisted.internet.error import CannotListenError

from pulse2.package_server.server import P2PSite
from pulse2.package_server.description import Description
from pulse2.package_server.common import Common
from pulse2.package_server.mirror_api import MirrorApi
from pulse2.package_server.scheduler_api import SchedulerApi
from pulse2.package_server.mirror import Mirror
from pulse2.package_server.package_api_get import PackageApiGet
from pulse2.package_server.package_api_put import PackageApiPut
from pulse2.package_server.user_package_api import UserPackageApi
from pulse2.package_server.imaging.api import ImagingApi
from pulse2.package_server.imaging.pxe.server import PXEProxy

import pulse2.xmlrpc


class MyServer(resource.Resource):
    def register(self, klass, mp):
        mp = re.compile("^/").sub("", mp)
        if isinstance(mp, str):
            mp = mp.encode("utf-8")
        return self.putChild(mp, klass)


def initialize(config):
    """
    Init package server API, and start listening to the network.

    @rtype: bool
    @return: return False if initialization failed
    """
    ret = True
    logger = logging.getLogger()

    port = int(config.port)

    server = MyServer()
    services = []
    if len(config.mirrors) > 0:
        for mirror_params in config.mirrors:
            # If source dosesnt exist, create it
            if not os.path.isdir(mirror_params["src"]):
                os.mkdir(mirror_params["src"])
            m_api = Mirror(mirror_params["mount_point"], mirror_params["mount_point"])
            server.register(m_api, mirror_params["mount_point"])
            services.append(
                {
                    "type": "mirror",
                    "mp": mirror_params["mount_point"],
                    "server": config.public_ip,
                    "port": config.port,
                    "proto": config.proto,
                    "src": mirror_params["src"],
                    "mirror_mp": "%s_files" % (mirror_params["mount_point"]),
                    "mirror_url": "%s://%s:%s%s_files"
                    % (
                        config.proto,
                        config.public_ip,
                        config.port,
                        mirror_params["mount_point"],
                    ),
                    "url": "%s://%s:%s%s"
                    % (
                        config.proto,
                        config.public_ip,
                        config.port,
                        mirror_params["mount_point"],
                    ),
                }
            )
            server.register(
                static.File(mirror_params["src"]),
                mirror_params["mount_point"] + "_files",
            )
            services.append(
                {
                    "type": "mirror_files",
                    "mp": mirror_params["mount_point"] + "_files",
                    "server": config.public_ip,
                    "port": config.port,
                    "proto": config.proto,
                    "src": mirror_params["src"],
                }
            )

    if len(config.package_api_get) > 0:
        for mirror_params in config.package_api_get:
            p_api = PackageApiGet(
                mirror_params["mount_point"], mirror_params["mount_point"]
            )
            server.register(p_api, mirror_params["mount_point"])
            services.append(
                {
                    "type": "package_api_get",
                    "mp": mirror_params["mount_point"],
                    "server": config.public_ip,
                    "port": config.port,
                    "proto": config.proto,
                    "src": mirror_params["src"],
                    "url": "%s://%s:%s%s"
                    % (
                        config.proto,
                        config.public_ip,
                        config.port,
                        mirror_params["mount_point"],
                    ),
                }
            )

    if len(config.package_api_put) > 0:
        for mirror_params in config.package_api_put:
            p_api = PackageApiPut(
                mirror_params["mount_point"],
                mirror_params["mount_point"],
                mirror_params["tmp_input_dir"],
            )
            server.register(p_api, mirror_params["mount_point"])
            services.append(
                {
                    "type": "package_api_put",
                    "mp": mirror_params["mount_point"],
                    "server": config.public_ip,
                    "port": config.port,
                    "proto": config.proto,
                    "src": mirror_params["src"],
                    "url": "%s://%s:%s%s"
                    % (
                        config.proto,
                        config.public_ip,
                        config.port,
                        mirror_params["mount_point"],
                    ),
                }
            )

    if "mount_point" in config.user_package_api:
        mirror = UserPackageApi(
            services, config.user_package_api["mount_point"], config.up_assign_algo
        )
        server.register(mirror, config.user_package_api["mount_point"])
        services.append(
            {
                "type": "user_package_api",
                "mp": config.user_package_api["mount_point"],
                "server": config.public_ip,
                "port": config.port,
                "proto": config.proto,
            }
        )

    if "mount_point" in config.mirror_api:
        mirror = MirrorApi(
            services, config.mirror_api["mount_point"], config.mm_assign_algo
        )
        server.register(mirror, config.mirror_api["mount_point"])
        services.append(
            {
                "type": "mirror_api",
                "mp": config.mirror_api["mount_point"],
                "server": config.public_ip,
                "port": config.port,
                "proto": config.proto,
            }
        )
    else:
        logger.warn("package server initialized without mirror api")

    if "mount_point" in config.scheduler_api:
        scheduler = SchedulerApi(
            config.scheduler_api["mount_point"], config.scheduler_api
        )
        server.register(scheduler, config.scheduler_api["mount_point"])
        services.append(
            {
                "type": "scheduler_api",
                "mp": config.scheduler_api["mount_point"],
                "server": config.public_ip,
                "port": config.port,
                "proto": config.proto,
            }
        )
        logger.info("package server initialized with scheduler api")

    if config.imaging_api:
        try:
            imaging = ImagingApi(config.imaging_api["mount_point"], config)
            server.register(imaging, config.imaging_api["mount_point"])
            services.append(
                {
                    "type": "imaging",
                    "mp": config.imaging_api["mount_point"],
                    "server": config.public_ip,
                    "port": config.port,
                    "proto": config.proto,
                }
            )
            logger.info("Package Server initialized with imaging API")
            try:
                PXEProxy(config, imaging.api)
            except CannotListenError:
                logger.error("PXE proxy: start failed")
                logger.error(
                    "PXE Proxy: Adress already in use: old LRS imaging-server still installed and not yet stopped"
                )
                logger.error(
                    "PXE proxy: Please verify your configuration and restart the service"
                )

            except Exception as e:
                logger.exception("Imaging error: %s" % e)
                logger.error("PXE imaging service initialization failed, exiting.")
            else:
                logger.info("Package Server initialized with PXE imaging API")

        except Exception as e:
            logger.exception("Imaging error: %s" % e)
            logger.error("Error while initializing the imaging API")
            logger.error("Package Server will run WITHOUT the imaging API")

    desc = Description(services)
    server.register(desc, "/desc")
    Common().setDesc(services)

    try:
        if config.enablessl:
            pulse2.xmlrpc.OpenSSLContext().setup(
                config.localcert, config.cacert, config.verifypeer
            )
            twisted.internet.reactor.listenSSL(
                port,
                P2PSite(server),
                interface=config.bind,
                contextFactory=pulse2.xmlrpc.OpenSSLContext().getContext(),
            )
            logger.info("activating SSL mode")
        else:
            twisted.internet.reactor.listenTCP(
                port, twisted.web.server.Site(server), interface=config.bind
            )
        logger.info("package server listening on %s:%d" % (config.bind, port))
    except Exception as e:
        logger.error("can't bind to %s:%d" % (config.bind, port))
        logger.error(e)
        ret = False

    return ret
