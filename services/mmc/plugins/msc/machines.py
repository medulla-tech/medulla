# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
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

import logging
from mmc.plugins.msc.config import MscConfig
from mmc.plugins.base.computers import ComputerManager
from mmc.support.mmctools import Singleton

class Machine:
    def __init__(self, h_params):
        self.config = MscConfig()
        self.logger = logging.getLogger()
        self.logger.debug("new machine: |%s|" % h_params)
        self.ip = None
        try:
            self.hostname = h_params['cn']
        except:
            try:
                self.hostname = h_params['hostname'][0]
            except:
                self.hostname = '???'
        try:
            self.uuid = h_params['objectUUID'][0]
        except:
            self.uuid = None
        try:
            self.displayname = h_params['displayName'][0]
        except:
            self.displayname = self.hostname
        try:
            self.fullname = h_params['fullname']
        except:
            self.fullname = self.hostname
        self.platform = ''

    def toH(self):
        return {'hostname':self.hostname, 'uuid':self.uuid, 'displayName':self.displayname, 'fullname':self.fullname}

    def getPlatform(self):
        # FIXME: please use the scheduler
        return ''

    def ping(self):
        # FIXME: please use the scheduler
        return False

class Machines(Singleton):
    def __init__(self):
        self.logger = logging.getLogger()
        self.config = MscConfig()

    def getAllMachines(self, ctx):
        """
        return all declared machines
        """
        ret = ComputerManager().getComputersList(ctx)
        return map(lambda m: Machine(ret[m][1]), ret)

    def getMachines(self, ctx, h_params):
        """
        return a list of machine matching with params
        h_params stuct looks like that : {'hostname':name, 'uuid':uuid}
        """
        ret = ComputerManager().getComputersList(ctx, h_params)
        return map(lambda m: Machine(ret[m][1]), ret)

    def getMachine(self, ctx, h_params):
        """
        return only one machine (the first matching with params)
        h_params stuct looks like that : {'hostname':name, 'uuid':uuid}
        """
        try:
            ret = ComputerManager().getComputer(ctx, h_params)
            self.logger.debug("getMachine: wanted |%s|, got |%s|" % (h_params, ret))
            if ret != None:
                if ret != False:
                    if type(ret) == list:
                        return Machine(ret[1])
                    else:
                        return Machine(ret)
                else:
                    return None
        except KeyError:
            pass
            
        ret = ComputerManager().getComputersList(ctx, h_params)
        self.logger.debug("getMachine: wanted |%s|, got |%s|" % (h_params, ret))
        try:
            self.logger.debug(ret[h_params['hostname']][1])
            return Machine(ret[h_params['hostname']][1])
        except:
            return None
