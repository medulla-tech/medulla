# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# big modules
import logging
import os.path  # for SSL cert files checking

from mmc.support.config import PluginConfig
from pulse2.xmlrpc import isTwistedEnoughForLoginPass


class PkgsConfig(PluginConfig):
    # User/package_api API stuff
    upaa_server = "127.0.0.1"
    upaa_port = "9990"
    upaa_mountpoint = "/upaa"
    upaa_username = ""
    upaa_password = ""
    upaa_enablessl = True
    upaa_verifypeer = False
    upaa_cacert = ""
    upaa_localcert = ""
    tmp_dir = os.path.join("/tmp", "pkgs_tmp")

    # Appstream settings
    appstream_url = ""

    def readConf(self):
        """
        Read the module configuration
        """
        PluginConfig.readConf(self)
        self.dbdriver = self.get("database", "dbdriver")
        self.dbhost = self.get("database", "dbhost")
        self.dbname = self.get("database", "dbname")
        self.dbuser = self.get("database", "dbuser")
        if self.has_option("database", "dbport"):
            self.dbport = self.getint("database", "dbport")
        else:
            self.dbport = 3306
        if self.has_option("database", "dbqueryecho"):
            self.dbqueryecho = self.getboolean("database", "dbqueryecho")
        else:
            self.dbqueryecho = False

        self.max_size_stanza_xmpp = 1048576
        if self.has_option("quick_deploy", "max_size_stanza_xmpp"):
            self.max_size_stanza_xmpp = self.getint(
                "quick_deploy", "max_size_stanza_xmpp"
            )

        self.dbsslenable = False
        if self.has_option("database", "dbsslenable"):
            self.dbsslenable = self.getboolean("database", "dbsslenable")
            if self.dbsslenable:
                self.dbsslca = self.get("database", "dbsslca")
                self.dbsslcert = self.get("database", "dbsslcert")
                self.dbsslkey = self.get("database", "dbsslkey")

        if self.has_option("database", "dbpooltimeout"):
            self.dbpooltimeout = self.getint("database", "dbpooltimeout")
        else:
            self.dbpooltimeout = 30

        if self.has_option("database", "dbpoolrecycle"):
            self.dbpoolrecycle = self.getint("database", "dbpoolrecycle")
        else:
            self.dbpoolrecycle = 60
        if self.has_option("database", "dbpoolsize"):
            self.dbpoolsize = self.getint("database", "dbpoolsize")
        else:
            self.dbpoolsize = 5
        self.dbpasswd = self.getpassword("database", "dbpasswd")

        # API Package
        if self.has_option("user_package_api", "server"):
            self.upaa_server = self.get("user_package_api", "server")
        if self.has_option("user_package_api", "port"):
            self.upaa_port = self.get("user_package_api", "port")
        if self.has_option("user_package_api", "mountpoint"):
            self.upaa_mountpoint = self.get("user_package_api", "mountpoint")

        if self.has_option("user_package_api", "username"):
            if not isTwistedEnoughForLoginPass():
                logging.getLogger().warning(
                    "your version of twisted is not high enough to use login (user_package_api/username)"
                )
                self.upaa_username = ""
            else:
                self.upaa_username = self.get("user_package_api", "username")
        if self.has_option("user_package_api", "password"):
            if not isTwistedEnoughForLoginPass():
                logging.getLogger().warning(
                    "your version of twisted is not high enough to use password (user_package_api/password)"
                )
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
            if (
                self.upaa_verifypeer
            ):  # we need twisted.internet.ssl.Certificate to activate certs
                if self.has_option("user_package_api", "cacert"):
                    self.upaa_cacert = self.get("user_package_api", "cacert")
                if self.has_option("user_package_api", "localcert"):
                    self.upaa_localcert = self.get("user_package_api", "localcert")
                if not os.path.isfile(self.upaa_localcert):
                    raise Exception('can\'t read SSL key "%s"' % (self.upaa_localcert))
                if not os.path.isfile(self.upaa_cacert):
                    raise Exception(
                        'can\'t read SSL certificate "%s"' % (self.upaa_cacert)
                    )
                import twisted.internet.ssl

                if not hasattr(twisted.internet.ssl, "Certificate"):
                    raise Exception(
                        "I need at least Python Twisted 2.5 to handle peer checking"
                    )

        # Appstream settings
        if self.has_option("appstream", "url"):
            self.appstream_url = self.get("appstream", "url")

        # PKGS PARAMETERS
        self.centralizedmultiplesharing = False
        if self.has_option("pkgs", "centralizedmultiplesharing"):
            self.centralizedmultiplesharing = self.getboolean(
                "pkgs", "centralizedmultiplesharing"
            )
        self.movepackage = False
        if self.has_option("pkgs", "movepackage"):
            self.movepackage = self.getboolean("pkgs", "movepackage")

        self.generate_hash = False
        if self.has_option("integrity_checks", "generate_hash"):
            self.generate_hash = self.getboolean("integrity_checks", "generate_hash")

        self.hashing_algo = "SHA256"
        if self.has_option("integrity_checks", "hashing_algo"):
            self.hashing_algo = self.get("integrity_checks", "hashing_algo")

        self.keyAES32 = "abcdefghijklnmopqrstuvwxyz012345"
        if self.has_option("integrity_checks", "keyAES32"):
            self.keyAES32 = self.get("integrity_checks", "keyAES32")
