# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Inventory implementation of the Computer Interface
Used by the ComputerManager
"""

from mmc.plugins.base import ComputerI
from mmc.plugins.inventory.config import InventoryConfig
from pulse2.database.inventory import Inventory
from pulse2.managers.imaging import ComputerImagingManager
import pulse2.utils
import logging


class InventoryComputers(ComputerI):
    def __init__(self, conffile=None):
        self.logger = logging.getLogger()
        self.config = InventoryConfig()
        self.inventory = Inventory()

    def getComputer(self, ctx, filt=None, empty_macs=False):
        ret = self.inventory.getMachinesOnly(ctx, filt)

        if isinstance(ret, list) and len(ret) == 1:
            return ret[0].toDN(ctx, True)
        else:
            return {}

    def getMachineMac(self, ctx, filt):  # TODO : need to sort!
        """
        @return: dict of computer with their MAC addresses
                 {'UUID1', ['MAC1', 'MAC2'], 'UUID2': ['MAC1']}
        """
        machines = self.inventory.getMachineNetwork(ctx, filt)
        ret = {}
        for m in machines:
            ret[m[2]] = []
            for net in m[1]:
                ret[m[2]].append(net["MACAddress"])
        return ret

    def getMachineIp(self, ctx, filt):  # TODO : need to sort!
        machines = self.inventory.getMachineNetwork(ctx, filt)
        ret = []
        for m in machines:
            ret.append([i["IP"] for i in m[1]])
        if len(ret) == 1:
            return ret[0]
        return ret

    def getMachineHostname(self, ctx, filt=None):
        machines = self.inventory.getMachinesOnly(ctx, filt)
        ret = []
        for m in machines:
            ret.append(m.toH())
        if len(ret) == 1:
            return ret[0]
        return ret

    def getComputersNetwork(self, ctx, filt):
        computers = self.inventory.getMachinesNetworkSorted(ctx, filt)
        ret = []
        for item in computers:
            tmp = [False, {"cn": [item[0]], "objectUUID": [item[2]]}]
            # if not item[1]:
            if not len(item[1]):
                tmp[1]["ipHostNumber"] = ""
                tmp[1]["macAddress"] = ""
                tmp[1]["subnetMask"] = ""
                tmp[1]["networkUuids"] = ""
            else:
                tmp[1]["ipHostNumber"] = item[1]["IP"]
                tmp[1]["macAddress"] = item[1]["MACAddress"]
                tmp[1]["subnetMask"] = item[1]["SubnetMask"]
                tmp[1]["networkUuids"] = item[1]["networkUuids"]
            ret.append(tmp)
        return ret

    def getComputersList(self, ctx, filt=None):
        return self.getRestrictedComputersList(ctx, 0, -1, filt)

    def __restrictLocationsOnImagingServerOrEntity(self, filt, ctx):
        if "imaging_server" in filt and filt["imaging_server"] != "":
            # Get main imaging entity uuid
            self.logger.debug(
                "Get main imaging entity UUID of imaging server %s"
                % filt["imaging_server"]
            )
            main_imaging_entity_uuid = (
                ComputerImagingManager().getImagingServerEntityUUID(
                    filt["imaging_server"]
                )
            )
            if main_imaging_entity_uuid != None:
                self.logger.debug("Found: %s" % main_imaging_entity_uuid)
                filt["imaging_entities"] = [main_imaging_entity_uuid]
                self.logger.debug(
                    "Get now children entities of this main imaging entity"
                )
                # Get childs entities of this main_imaging_entity_uuid
                # Search only in user context
                for loc in self.inventory.getUserLocations(ctx.userid):
                    if ComputerImagingManager().isChildOfImagingServer(
                        loc.uuid, main_imaging_entity_uuid
                    ):
                        self.logger.debug(
                            "Found %s as child entity of %s"
                            % (loc.uuid, main_imaging_entity_uuid)
                        )
                        filt["imaging_entities"].append(loc.uuid)
            else:
                self.logger.warn(
                    "can't get the entity that correspond to the imaging server %s"
                    % (filt["imaging_server"])
                )
                return [False]

        if "imaging_entities" in filt:
            grep_entity = []
            for l in ctx.locations:
                if l.uuid in filt["imaging_entities"]:
                    grep_entity.append(l)
            if grep_entity:
                filt["ctxlocation"] = grep_entity
            else:
                self.logger.warn(
                    "the user '%s' try to filter on an entity he shouldn't access '%s'"
                    % (ctx.userid, filt["entity_uuid"])
                )
                return [False]
        return [True, filt]

    def getRestrictedComputersListLen(self, ctx, filt={}):
        if filt == "" or filt is None:
            filt = {}

        filt = self.__restrictLocationsOnImagingServerOrEntity(filt, ctx)
        if not filt[0]:
            return 0
        filt = filt[1]

        return self.inventory.countMachinesOnly(ctx, filt)

    def getRestrictedComputersList(
        self, ctx, min=0, max=-1, filt={}, advanced=True, justId=False, toH=False
    ):
        if filt == "" or filt is None:
            filt = {}

        filt = self.__restrictLocationsOnImagingServerOrEntity(filt, ctx)
        if not filt[0]:
            return {}
        filt = filt[1]

        filt["min"] = min
        filt["max"] = max

        if "imaging_entities" in filt:  # imaging group creation
            machines_uuids = [
                m.uuid() for m in self.inventory.getMachinesOnly(ctx, filt)
            ]
            # display only "imaging compliant" computers
            uuids = []
            networks = self.getComputersNetwork(ctx, {"uuids": machines_uuids})
            for network in networks:
                network = network[1]
                # Check if computer has macAddress and ipHostNumber
                if network["macAddress"] and network["ipHostNumber"]:
                    uuids.append(network["objectUUID"][0])
                else:
                    logging.getLogger().debug(
                        "Computer %s cannot be added in an imaging group:"
                        % network["cn"]
                    )
                    if not network["macAddress"]:
                        logging.getLogger().debug("No MAC found !")
                    if not network["ipHostNumber"]:
                        logging.getLogger().debug("No IP address found !")
            filt["uuids"] = uuids

        if justId:
            return [m.uuid() for m in self.inventory.getMachinesOnly(ctx, filt)]
        elif toH:
            return [m.toH() for m in self.inventory.getMachinesOnly(ctx, filt)]
        else:
            if "get" in filt:
                return [
                    m.toCustom(filt["get"])
                    for m in self.inventory.getMachinesOnly(ctx, filt)
                ]
            else:
                return self.inventory.getComputersOptimized(ctx, filt)

    def getTotalComputerCount(self):
        return self.inventory.getTotalComputerCount()

    def getComputerCount(self, ctx, filt=None):
        return self.getRestrictedComputersListLen(ctx, filt)

    def canAddComputer(self):
        return self.inventory.canAddMachine()

    def canAssociateComputer2Location(self):
        return True

    def addComputer(self, ctx, params):
        name = params["computername"]
        comment = params["computerdescription"].encode("utf-8")
        ip = params["computerip"]
        mac = params["computermac"]
        net = params["computernet"]
        location = None
        if "location_uuid" in params:
            location = params["location_uuid"]
        ret = self.inventory.addMachine(name, ip, mac, net, comment, location)
        return ret

    def neededParamsAddComputer(self):
        return [
            ["computerip", "string", "Computer's IP address"],
            ["computermac", "string", "Computer's MAC address"],
            ["computernet", "string", "Computer's netmask address"],
        ]

    def checkComputerName(self, name):
        return pulse2.utils.checkComputerName(name)

    def isComputerNameAvailable(self, ctx, locationUUID, name):
        return self.inventory.isComputerNameAvailable(ctx, locationUUID, name)

    def canDelComputer(self):
        return True

    def delComputer(self, ctx, uuid, backup):
        return self.inventory.delMachine(uuid)

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
        return self.inventory.editMachineName(uuid, name)

    def getComputerByMac(self, mac):
        ret = self.inventory.getMachinesBy(None, "Network", "MACAddress", mac, False)
        if isinstance(ret, list):
            if len(ret) != 0:
                return ret[0]
            else:
                return None
        return ret

    def getComputersOS(self, uuids):
        return self.inventory.getComputersOS(uuids)

    def getComputersListHeaders(self, ctx):
        """
        Computers list header is just hostname as Computer Name and Description as Description
        """
        return self.config.display

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
        return self.inventory.getMachineByHostnameAndMacs(ctx, hostname, macs)
