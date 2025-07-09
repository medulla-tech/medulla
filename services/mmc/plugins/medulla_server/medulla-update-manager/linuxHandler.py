#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2011-2012 Mandriva, http://www.mandriva.com/
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.
# linuxHandler.py

import sys
import subprocess
from abc import ABCMeta, abstractmethod

class linuxUpdateHandler(object, metaclass=ABCMeta):
    platform = None
    distro_infos = None
    def __init__(self, distro_infos):
        self.distro_id = distro_infos["id"]
        self.distro_version = distro_infos["version"]
        self.distro_name = distro_infos["name"]

    def runinshell(self, cmd, fatal=True, out_when_error=None):
        process = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        # Décodage ici — une bonne fois pour toutes
        out = out.decode("utf-8").strip()
        err = err.decode("utf-8").strip()
        if fatal and process.returncode != 0:
            sys.stdout.write(out)
            sys.stderr.write(err)
            sys.exit(process.returncode)
        if out_when_error is not None and process.returncode != 0:
            out = out_when_error
        return out, err, process.returncode
    @abstractmethod
    def disableNativeUpdates(self):
        pass
    @abstractmethod
    def showUpdateInfo(self, uuid, online=True):
        pass
    @abstractmethod
    def getAvailableUpdates(self, online=True, returnResultList=False):
        pass
    @abstractmethod
    def installUpdates(self, uuid_list):
        pass