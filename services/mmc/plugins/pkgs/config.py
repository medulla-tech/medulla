# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id: config.py 90 2008-06-06 12:35:08Z cdelfosse $
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# big modules
import logging
import os.path # for SSL cert files checking

from mmc.support.config import PluginConfig
from pulse2.xmlrpc import isTwistedEnoughForLoginPass

class PkgsConfig(PluginConfig):

    # User/package_api API stuff
    upaa_server = "127.0.0.1"
    upaa_port = "9990"
    upaa_mountpoint = "/upaa"
    upaa_username = ''
    upaa_password = ''
    upaa_enablessl = True
    upaa_verifypeer = False
    upaa_cacert = ''
    upaa_localcert = ''
    tmp_dir = os.path.join('/tmp', 'pkgs_tmp')

    def readConf(self):
        """
        Read the module configuration
        """
        PluginConfig.readConf(self)

        # API Package
        if self.has_option("user_package_api", "server"):
            self.upaa_server = self.get("user_package_api", "server")
        if self.has_option("user_package_api", "port"):
            self.upaa_port = self.get("user_package_api", "port")
        if self.has_option("user_package_api", "mountpoint"):
            self.upaa_mountpoint = self.get("user_package_api", "mountpoint")

        if self.has_option("user_package_api", "username"):
            if not isTwistedEnoughForLoginPass():
                logging.getLogger().warning("your version of twisted is not high enough to use login (user_package_api/username)")
                self.upaa_username = ""
            else:
                self.upaa_username = self.get("user_package_api", "username")
        if self.has_option("user_package_api", "password"):
            if not isTwistedEnoughForLoginPass():
                logging.getLogger().warning("your version of twisted is not high enough to use password (user_package_api/password)")
                self.upaa_password = ""
            else:
                self.upaa_password = self.get("user_package_api", "password")
        if self.has_option("user_package_api", "tmp_dir"):
            self.tmp_dir = self.get("user_package_api", "tmp_dir")
        if self.has_option("user_package_api", "enablessl"):
            self.upaa_enablessl = self.getboolean("user_package_api", "enablessl")

        if self.upaa_enablessl:
            if self.has_option("user_package_api", "verifypeer"):
                self.upaa_verifypeer = self.getboolean("user_package_api", "verifypeer")
            if self.upaa_verifypeer: # we need twisted.internet.ssl.Certificate to activate certs
                if self.has_option("user_package_api", "cacert"):
                    self.upaa_cacert = self.get("user_package_api", "cacert")
                if self.has_option("user_package_api", "localcert"):
                    self.upaa_localcert = self.get("user_package_api", "localcert")
                if not os.path.isfile(self.upaa_localcert):
                    raise Exception('can\'t read SSL key "%s"' % (self.upaa_localcert))
                if not os.path.isfile(self.upaa_cacert):
                    raise Exception('can\'t read SSL certificate "%s"' % (self.upaa_cacert))
                import twisted.internet.ssl
                if not hasattr(twisted.internet.ssl, "Certificate"):
                    raise Exception('I need at least Python Twisted 2.5 to handle peer checking')
