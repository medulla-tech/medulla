#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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


import sys
import os
import os.path
import json
import logging
import bsddb

logger = logging.getLogger()


class manageschedulerdeploy:

    def __init__(self, namebase="BDtimedeploy"):
        name_basecmd = namebase + 'cmddb'
        name_basesession = namebase + 'sessiondb'
        self.openbool = False
        path_bd = self.bddir()
        if path_bd is not None:
            if not os.path.exists(path_bd):
                os.makedirs(path_bd, mode=0700)
            self.name_basesession = os.path.join(path_bd, name_basesession)
            self.name_basecmd = os.path.join(path_bd, name_basecmd)

    def openbase(self):
        self.dbcmdscheduler = bsddb.btopen(self.name_basecmd, 'c')
        self.dbsessionscheduler = bsddb.btopen(self.name_basesession, 'c')

    def closebase(self):
        self.dbcmdscheduler.close()
        self.dbsessionscheduler.close()

    def bddir(self):
        if sys.platform.startswith('linux'):
            return os.path.join("/", "var", "lib", "pulse2", "BDDeploy")
        elif sys.platform.startswith('win'):
            return os.path.join(os.environ["ProgramFiles"], "Pulse", "var", "tmp", "BDDeploy")
        elif sys.platform.startswith('darwin'):
            return os.path.join("/", "Library", "Application Support", "Pulse", "BDDeploy")
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
        if self.dbsessionscheduler.has_key(str(sessionid)):
            data = self.dbsessionscheduler[sessionid]
        self.closebase()
        return data

    def del_sesionscheduler(self, sessionid):
        sessionid = str(sessionid)
        self.openbase()
        if self.dbsessionscheduler.has_key(sessionid):
            del self.dbsessionscheduler[sessionid]
            self.dbsessionscheduler.sync()
        self.closebase()


# for k, v in db.iteritems():
# ...     print k, v
