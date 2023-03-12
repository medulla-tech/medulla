#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import sys
import os
import os.path
import logging
import bsddb

logger = logging.getLogger()


class manageschedulerdeploy:
    def __init__(self, namebase="BDtimedeploy"):
        name_basecmd = namebase + "cmddb"
        name_basesession = namebase + "sessiondb"
        self.openbool = False
        path_bd = self.bddir()
        if path_bd is not None:
            if not os.path.exists(path_bd):
                os.makedirs(path_bd, mode=0o700)
            self.name_basesession = os.path.join(path_bd, name_basesession)
            self.name_basecmd = os.path.join(path_bd, name_basecmd)

    def openbase(self):
        self.dbcmdscheduler = bsddb.btopen(self.name_basecmd, "c")
        self.dbsessionscheduler = bsddb.btopen(self.name_basesession, "c")

    def closebase(self):
        self.dbcmdscheduler.close()
        self.dbsessionscheduler.close()

    def bddir(self):
        if sys.platform.startswith("linux"):
            return os.path.join("/", "var", "lib", "pulse2", "BDDeploy")
        elif sys.platform.startswith("win"):
            return os.path.join(
                os.environ["ProgramFiles"], "Pulse", "var", "tmp", "BDDeploy"
            )
        elif sys.platform.startswith("darwin"):
            return os.path.join(
                "/", "Library", "Application Support", "Pulse", "BDDeploy"
            )
        else:
            return None

    def set_sesionscheduler(self, sessionid, objsession):
        sessionid = str(sessionid)
        self.openbase()
        self.dbsessionscheduler[sessionid] = objsession
        self.dbsessionscheduler.sync()
        self.closebase()

    def get_sesionscheduler(self, sessionid):
        sessionid = str(sessionid)
        data = ""
        self.openbase()
        if str(sessionid) in self.dbsessionscheduler:
            data = self.dbsessionscheduler[sessionid]
        self.closebase()
        return data

    def del_sesionscheduler(self, sessionid):
        sessionid = str(sessionid)
        self.openbase()
        if sessionid in self.dbsessionscheduler:
            del self.dbsessionscheduler[sessionid]
            self.dbsessionscheduler.sync()
        self.closebase()


# for k, v in db.iteritems():
# ...     print k, v
