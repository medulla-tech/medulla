# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from mmc.support.config import MMCConfigParser
from mmc.support.mmctools import Singleton


class DatabaseConfig(Singleton):
    dbsection = "database"

    dbdriver = "mysql"
    dbhost = "127.0.0.1"
    dbname = None
    dbport = None
    dbuser = "mmc"
    dbpasswd = "mmc"

    dbdebug = "ERROR"
    dbpoolrecycle = 60
    dbpoolsize = 5
    dbpooltimeout = 30
    # SSL support
    dbsslenable = False
    dbsslca = None
    dbsslcert = None
    dbsslkey = None

    def setup(self, config_file):
        # Load configuration file
        self.cp = MMCConfigParser()
        self.cp.read(config_file)
        self.cp.read(config_file + ".local")

        if self.cp.has_section(self.dbsection):
            if self.cp.has_option(self.dbsection, "dbdriver"):
                self.dbdriver = self.cp.get(self.dbsection, "dbdriver")
            if self.cp.has_option(self.dbsection, "dbhost"):
                self.dbhost = self.cp.get(self.dbsection, "dbhost")
            if self.cp.has_option(self.dbsection, "dbport"):
                self.dbport = self.cp.getint(self.dbsection, "dbport")
            if self.cp.has_option(self.dbsection, "dbname"):
                self.dbname = self.cp.get(self.dbsection, "dbname")
            if self.cp.has_option(self.dbsection, "dbuser"):
                self.dbuser = self.cp.get(self.dbsection, "dbuser")
            if self.cp.has_option(self.dbsection, "dbpasswd"):
                self.dbpasswd = self.cp.getpassword(self.dbsection, "dbpasswd")

            if self.cp.has_option(self.dbsection, "dbdebug"):
                self.dbdebug = self.cp.get(self.dbsection, "dbdebug")

            if self.cp.has_option(self.dbsection, "dbpoolrecycle"):
                self.dbpoolrecycle = self.cp.getint(self.dbsection, "dbpoolrecycle")

            if self.cp.has_option(self.dbsection, "dbpoolsize"):
                self.dbpoolsize = self.cp.getint(self.dbsection, "dbpoolsize")

            if self.cp.has_option(self.dbsection, "dbpooltimeout"):
                self.dbpooltimeout = self.cp.getint(self.dbsection, "dbpooltimeout")

            if self.cp.has_option(self.dbsection, "dbsslenable"):
                self.dbsslenable = self.cp.getboolean(self.dbsection, "dbsslenable")
                if self.dbsslenable:
                    self.dbsslca = self.cp.get(self.dbsection, "dbsslca")
                    self.dbsslcert = self.cp.get(self.dbsection, "dbsslcert")
                    self.dbsslkey = self.cp.get(self.dbsection, "dbsslkey")
