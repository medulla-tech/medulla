# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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
            self.hostname = h_params["cn"]
        except:
            try:
                self.hostname = h_params["hostname"][0]
            except:
                self.hostname = "???"
        try:
            self.uuid = h_params["objectUUID"][0]
        except:
            self.uuid = None
        try:
            self.displayname = h_params["displayName"][0]
        except:
            self.displayname = self.hostname
        try:
            self.fullname = h_params["fullname"]
        except:
            self.fullname = self.hostname
        self.platform = ""

    def toH(self):
        return {
            "hostname": self.hostname,
            "uuid": self.uuid,
            "displayName": self.displayname,
            "fullname": self.fullname,
        }

    def getPlatform(self):
        # FIXME: please use the scheduler
        return ""

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
        return [Machine(ret[m][1]) for m in ret]

    def getMachines(self, ctx, h_params):
        """
        return a list of machine matching with params
        h_params stuct looks like that : {'hostname':name, 'uuid':uuid}
        """
        ret = ComputerManager().getComputersList(ctx, h_params)
        return [Machine(ret[m][1]) for m in ret]

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
                    if isinstance(ret, list):
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
            self.logger.debug(ret[h_params["hostname"]][1])
            return Machine(ret[h_params["hostname"]][1])
        except:
            return None
