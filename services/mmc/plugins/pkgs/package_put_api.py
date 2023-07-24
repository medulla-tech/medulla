# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
This module define the package put API
It provides methods to modify the content of packages.
"""
import logging
import pulse2.apis.clients.package_put_api


class PackagePutA(pulse2.apis.clients.package_put_api.PackagePutA):
    def __init__(self, server, port=None, mountpoint=None, proto="http", login=""):
        self.logger = logging.getLogger()
        credentials = ""
        if isinstance(server, dict):
            mountpoint = server["mountpoint"]
            port = server["port"]
            proto = server["protocol"]
            bind = server["server"]
            if (
                "username" in server
                and "password" in server
                and server["username"] != ""
            ):
                # if 'username' in server and 'password' in server and server['username'] != '':
                login = "%s:%s@" % (server["username"], server["password"])
                credentials = "%s:%s" % (server["username"], server["password"])

        self.server_addr = "%s://%s%s:%s%s" % (
            proto,
            login,
            bind,
            str(port),
            mountpoint,
        )
        self.logger.debug("PackagePutA will connect to %s" % (self.server_addr))

        self.config = mmc.plugins.pkgs.PkgsConfig("pkgs")
        if self.config.upaa_verifypeer:
            pulse2.apis.clients.package_put_api.PackagePutA.__init__(
                self,
                credentials,
                self.server_addr,
                self.config.upaa_verifypeer,
                self.config.upaa_cacert,
                self.config.upaa_localcert,
            )
        else:
            pulse2.apis.clients.package_put_api.PackagePutA.__init__(
                self, credentials, self.server_addr
            )
