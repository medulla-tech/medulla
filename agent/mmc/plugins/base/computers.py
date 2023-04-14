# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Computer Manager is used to call methods giving informations on computers whatever is the computer backend.

"""
import logging
from mmc.support.mmctools import Singleton, SingletonN


class ComputerI:
    __metaclass__ = SingletonN

    def canAddComputer(self):
        """
        Does this module handle addition of computers
        """
        pass

    def canAssociateComputer2Location(self):
        """
        Does this module handle association between computers and locations
        """
        pass

    def addComputer(self, ctx, params):
        """
        Add a new computer
        """
        pass

    def checkComputerName(self, name):
        """
        Ask to all plugins that can add computer if the given name is a valid
        computer name.

        @param name: computer name to check
        @type name: str

        @returns: whether the computer name is valid or not
        @rtype: bool
        """
        pass

    def isComputerNameAvailable(self, ctx, locationUUID, name):
        """
        Ask if the hostname is already used in that entity to know if it's a duplicate
        or not

        @param ctx: the context
        @type:

        @param locationUUID: the entity uuid
        @type: str

        @param name: the computer name to check
        @type: str

        @returns: True is the hostname is available
        @rtype: bool
        """
        pass

    def canDelComputer(self):
        """
        Does this module handle removal of computers
        """
        pass

    def delComputer(self, ctx, uuid, backup):
        """
        Del a computer
        """
        pass

    def editComputerName(self, ctx, uuid, name):
        """
        Edit the computer name

        @param ctx: the context
        @type: currentContext

        @param uuid: the machine uuid
        @type: str

        @param name: new computer name
        @type: str

        @returns: True if the name changed
        @rtype: bool
        """
        pass


    def getComputer(self, ctx, params, empty_macs=False):
        """
        Get only one computer
        """
        pass

    def getComputersNetwork(self, ctx, filt):
        """
        Get the computers network
        """
        pass

    def getMachineMac(self, ctx, params):
        """
        Get the computers mac adresses
        """
        pass

    def getMachineIp(self, ctx, params):
        """
        Get the computers ip addresses
        """
        pass

    def getMachineHostname(self, ctx, params):
        """
        Get the computers hostnames
        """
        pass

    def getComputerList(self, ctx, params):
        """
        Get computer list
        """
        pass

    def getComputerCount(self, ctx, params = None):
        """
        Get the number of computer
        """
        pass

    def getTotalComputerCount(self):
        """
        Get the computer full count (not depending of
        the user context)
        """
        pass

    def getRestrictedComputersListLen(self, ctx, params):
        """
        Get a limited computer list size
        """
        pass

    def getRestrictedComputersList(self, ctx, params):
        """
        Get a limited computer list
        """
        pass

    def getComputerByMac(self, mac):
        """
        Get the computer who have that mac address
        send a list with possibly more than one computer
        """
        pass

    def getComputersOS(self, uuids):
        """
        Get OS for a given computer
        """
        pass

    def getComputersListHeaders(self, ctx):
        """
        Get the headers of the computer list
        """
        pass


class ComputerManager(Singleton):

    components = {}
    main = "none"

    def __init__(self):
        Singleton.__init__(self)
        self.logger = logging.getLogger()

    def select(self, name):
        self.logger.info(f"Selecting computer manager: {name}")
        self.main = name

    def getManagerName(self):
        return self.main

    def isActivated(self):
        return (self.main != 'none')


    def register(self, name, klass):
        self.logger.debug(f"Registering computer manager {name} / {str(klass)}")
        self.components[name] = klass

    def validate(self):
        ret = (self.main == "none") or (self.main in self.components)
        if not ret:
            self.logger.error(f"Selected computer manager '{self.main}' not available")
            self.logger.error("Please check that the corresponding plugin was successfully enabled")
        return ret

    def canAddComputer(self):
        klass = self.components[self.main]
        return klass().canAddComputer()

    def canDelComputer(self):
        klass = self.components[self.main]
        return klass().canDelComputer()

    def canAssociateComputer2Location(self):
        klass = self.components[self.main]
        instance = klass()
        if hasattr(instance, 'canAssociateComputer2Location'):
            return instance.canAssociateComputer2Location()
        return False

    def addComputer(self, ctx, params):
        r = None
        for plugin in self.components:
            klass = self.components[plugin]
            instance = klass()
            if klass().canAddComputer():
                ret = instance.addComputer(ctx, params)
                if plugin == self.main:
                    r = ret
        return r

    def checkComputerName(self, name):
        ret = True
        for plugin in self.components:
            self.logger.debug(plugin)
            klass = self.components[plugin]
            instance = klass()
            if instance.canAddComputer() and not instance.checkComputerName(name):
                ret = False
                break
        return ret

    def isComputerNameAvailable(self, ctx, locationUUID, name):
        ret = True
        for plugin in self.components:
            self.logger.debug(plugin)
            klass = self.components[plugin]
            instance = klass()
            if instance.canAddComputer() and not instance.isComputerNameAvailable(ctx, locationUUID, name):
                ret = False
                break
        return ret

    def delComputer(self, ctx, uuid, backup):
        for plugin in self.components:
            klass = self.components[plugin]
            instance = klass()
            if klass().canDelComputer():
                instance.delComputer(ctx, uuid, backup)

    def editComputerName(self, ctx, uuid, name):
        """
        Edit the computer name

        @param ctx: the context
        @type: currentContext

        @param uuid: the machine uuid
        @type: str

        @param name: new computer name
        @type: str

        @returns: True if the name changed
        @type: bool

        """
        for plugin in self.components:
            klass = self.components[plugin]
            instance = klass()
            instance.editComputerName(ctx, uuid, name)

    def neededParamsAddComputer(self):
        try:
            klass = self.components[self.main]
            return klass().neededParamsAddComputer()
        except:
            return []

    def getComputer(self, ctx, filt = None, empty_macs=False):
        self.logger.debug(f"getComputer {filt}")
        klass = self.components[self.main]
        instance = klass()
        return instance.getComputer(ctx, filt, empty_macs)

    def getMachineMac(self, ctx, filt = None):
        klass = self.components[self.main]
        instance = klass()
        return instance.getMachineMac(ctx, filt)

    def getMachineIp(self, ctx, filt = None):
        klass = self.components[self.main]
        instance = klass()
        return instance.getMachineIp(ctx, filt)

    def getMachineHostname(self, ctx, filt = None):
        klass = self.components[self.main]
        instance = klass()
        return instance.getMachineHostname(ctx, filt)

    def getComputersNetwork(self, ctx, filt = None):
        klass = self.components[self.main]
        instance = klass()
        return instance.getComputersNetwork(ctx, filt)

    def getComputersList(self, ctx, filt = None):
        klass = self.components[self.main]
        instance = klass()
        return instance.getComputersList(ctx, filt)

    def simple_computer_count(self):
        klass = self.components[self.main]
        instance = klass()
        return instance.simple_computer_count()

    def getComputerCount(self, ctx, filt = {}):
        # Mutable dict filt used as default argument to a method or function
        #filt = filt or {}
        klass = self.components[self.main]
        instance = klass()
        return instance.getComputerCount(ctx, filt)

    def getTotalComputerCount(self):
        klass = self.components[self.main]
        instance = klass()
        return instance.getTotalComputerCount()

    def getRestrictedComputersListLen(self, ctx, filt = None, advanced = True):
        klass = self.components[self.main]
        instance = klass()
        return instance.getRestrictedComputersListLen(ctx, filt)

    def getRestrictedComputersList(self, ctx, min = 0, max = -1, filt = None, advanced = True, justId = False, toH = False):
        min = int(min)
        max = int(max)
        klass = self.components[self.main]
        instance = klass()
        return instance.getRestrictedComputersList(ctx, min, max, filt, advanced, justId, toH)

    def getMachineforentityList(self,  min = 0, max = -1, filt = None ):
        min = int(min)
        max = int(max)
        klass = self.components[self.main]
        instance = klass()
        return instance.getMachineforentityList( min, max, filt)

    def getComputerByMac(self, mac):
        klass = self.components[self.main]
        instance = klass()
        return instance.getComputerByMac(mac)

    def getComputersOS(self, uuids):
        klass = self.components[self.main]
        instance = klass()
        return instance.getComputersOS(uuids)

    def getComputersListHeaders(self, ctx):
        klass = self.components[self.main]
        instance = klass()
        ret = instance.getComputersListHeaders(ctx)
        if ret is None:
            ret = [['cn', 'Computer Name'], ['displayName', 'Description']]
        return ret

    def getComputerByHostnameAndMacs(self, ctx, hostname, macs):
        """
        Get machine who match given hostname and at least one of macs

        @param ctx: context
        @type ctx: dict

        @param hostname: hostname of wanted machine
        @type hostname: str

        @param macs: list of macs
        @type macs: list

        @return: UUID of wanted machine or False
        @rtype: str or None
        """
        klass = self.components[self.main]
        instance = klass()
        return instance.getComputerByHostnameAndMacs(ctx, hostname, macs)

    def getComputerFilteredByCriterion(self, ctx, criterion, values, other=None):
        logging.getLogger().warning(222)
        klass = self.components[self.main]
        instance = klass()
        return instance.getComputerFilteredByCriterion(ctx, criterion, values)
