# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Pulse 2 Package Server Imaging API
"""
import logging

from pulse2.package_server.xmlrpc import MyXmlrpc
from pulse2.package_server.imaging.api.functions import Imaging


class ImagingApi (MyXmlrpc):

    myType = 'Imaging'

    def __init__(self, name, config):
        """
        @param config: Package server config
        @type config: P2PServerCP
        """
        MyXmlrpc.__init__(self)
        self.api = Imaging()
        self.api.init1(config)

        self.name = name
        self.logger = logging.getLogger('imaging')
        self.logger.info("Initializing %s" % self.myType)

    def xmlrpc_getActiveConvergenceForHost(self, uuid):
        return Imaging().getActiveConvergenceForHost(uuid)

    def xmlrpc_logClientAction(self, mac, level, phase, message):
        return self.api.logClientAction(mac, level, phase, message)

    def xmlrpc_computerMenuUpdate(self, mac):
        return self.api.computerMenuUpdate(mac)

    def xmlrpc_imagingServerStatus(self):
        return self.api.imagingServerStatus()

    def xmlrpc_computersRegister(self, computers):
        return self.api.computersRegister(computers)

    def xmlrpc_computerRegister(self, computerName, macAddress, imagingData=False, waitToBeInventoried=False):
        return self.api.computerRegister(computerName, macAddress, imagingData, waitToBeInventoried)

    def xmlrpc_computerUnregister(self, computerUUID, imageList, archive):
        return self.api.computerUnregister(computerUUID, imageList, archive)

    def xmlrpc_computerPrepareImagingDirectory(self, uuid, imagingData = False):
        return self.api.computerPrepareImagingDirectory(uuid, imagingData)

    def xmlrpc_computerUpdate(self, MACAddress):
        return self.api.computerUpdate(MACAddress)

    def xmlrpc_injectInventory(self, MACAddress, inventory):
        return self.api.injectInventory(MACAddress, inventory)

    def xmlrpc_getComputerByMac(self, MACAddress):
        return self.api.getComputerByMac(MACAddress)

    def xmlrpc_computersMenuSet(self, menus):
        return self.api.computersMenuSet(menus)

    def xmlrpc_imagingServerDefaultMenuSet(self, menu):
        return self.api.imagingServerDefaultMenuSet(menu)

    def xmlrpc_imageGetLogs(self, imageUUID):
        return self.api.imageGetLogs(imageUUID)

    def xmlrpc_computerCreateImageDirectory(self, mac):
        return self.api.computerCreateImageDirectory(mac)

    def xmlrpc_computerChangeDefaultMenuItem(self, mac, num):
        return self.api.computerChangeDefaultMenuItem(mac, num)

    def xmlrpc_getDefaultMenuItem(self, mac):
        return self.api.getDefaultMenuItem(mac)

    def xmlrpc_imageDone(self, computerMACAddress, imageUUID):
        return self.api.imageDone(computerMACAddress, imageUUID)

    def xmlrpc_imagingServerImageDelete(self, imageUUID):
        return self.api.imagingServerImageDelete(imageUUID)

    def xmlrpc_imagingServerISOCreate(self, imageUUID, size, title):
        return self.api.imagingServerISOCreate(imageUUID, size, title)

    def xmlrpc_imagingServermenuMulticast(self, objmenu):
        """
        """
        return self.api.imagingServermenuMulticast(objmenu)

    def xmlrpc_imagingClearMenu(self, objmenu):
        """
        """
        return self.api.imagingClearMenu(objmenu)

    ## Imaging server configuration
    def xmlrpc_check_process_multicast(self, objprocess):
        # controle execution process multicast
        return self.api.check_process_multicast(objprocess)

    def xmlrpc_check_process_multicast_finish(self, objprocess):
        return self.api.check_process_multicast_finish(objprocess)

    def xmlrpc_start_process_multicast(self,objprocess):
        # controle execution process multicast
        return self.api.start_process_multicast(objprocess)

    def xmlrpc_muticast_script_exist(self,objprocess):
        # controle execution process multicast
        return self.api.muticast_script_exist(objprocess)

    def xmlrpc_clear_script_multicast(self,objprocess):
        # controle execution process multicast
        return self.api.clear_script_multicast(objprocess)

    def xmlrpc_checkDeploymentUDPSender(self,objprocess):
        # check transfert starting multicast
        return self.api.checkDeploymentUDPSender(objprocess)


    def xmlrpc_stop_process_multicast(self,objprocess):
        # controle execution process multicast
        return self.api.stop_process_multicast(objprocess)

    def xmlrpc_SetMulticastMultiSessionParameters(self, Paramsmulticast):
        # controle parameters multicast
        return self.api.SetMulticastMultiSessionParameters(Paramsmulticast)

    def xmlrpc_GetMulticastMultiSessionParameters(self, location):
        # controle parameters multicast
        return self.api.GetMulticastMultiSessionParameters(location)

    def xmlrpc_ClearMulticastMultiSessionParameters(self, location):
        return self.api.ClearMulticastMultiSessionParameters(location)


    def xmlrpc_imagingServerConfigurationSet(self, conf):
        return self.api.imagingServerConfigurationSet(conf)

    def xmlrpc_createBootServiceFromPostInstall(self, script_file):
        return self.api.createBootServiceFromPostInstall(script_file)

    def xmlrpc_bsUnlinkShFile(self, datas):
        return self.api.bsUnlinkShFile(datas)

    def xmlrpc_getClonezillaParamsForTarget(self, computerUUID):
        return self.api.getClonezillaParamsForTarget(computerUUID)
