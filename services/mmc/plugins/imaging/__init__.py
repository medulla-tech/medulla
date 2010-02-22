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

"""
Class to manage imaging mmc-agent api
imaging plugin
"""

import logging
import os

import mmc.plugins.imaging.images
import mmc.plugins.imaging.iso
from mmc.support.mmctools import xmlrpcCleanup
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.plugins.imaging.config import ImagingConfig
from mmc.plugins.base.computers import ComputerManager
from pulse2.database.imaging import ImagingDatabase
from pulse2.database.imaging.types import *
from pulse2.apis.clients.imaging import ImagingApi

VERSION = "0.1"
APIVERSION = "0:0:0"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

NOAUTHNEEDED = ['computerRegister', 'imagingServerRegister', 'getComputerUUID']

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    """
    Run some tests to ensure the module is ready to operate.
    """
    logger = logging.getLogger()
    config = ImagingConfig()
    config.init("imaging")

    if config.disable:
        logger.warning("Plugin imaging: disabled by configuration.")
        return False
    # TODO: check images directories exists

    # initialise imaging database
    if not ImagingDatabase().activate(config):
        logger.warning("Plugin imaging: an error occured during the database initialization")
        return False
    return True

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s

class RpcProxy(RpcProxyI):
    """ XML/RPC Bindings """

    """ DEPRECATED """
    def getPublicImagesList():
        """
        Return a list of public images

        Only images names are returned
        """
        mylist = []
        for image in mmc.plugins.imaging.images.getPublicImages().values():
            mylist.append(image.name)
        return mylist

    def getPublicImageInfos(name):
        """
        Return some informations about an Image

        """
        return xmlrpcCleanup(mmc.plugins.imaging.images.Image(name).getRawInfo())

    def deletePublicImage(name):
        """
        delete an Image

        """
        mmc.plugins.imaging.images.Image(name).delete()

    def isAnImage(name):
        """
        Check if pub image is a real image

        """
        config = mmc.plugins.imaging.ImagingConfig("imaging")
        return mmc.plugins.imaging.images.hasImagingData(os.path.join(config.publicpath, name))

    def duplicatePublicImage(name, newname):
        """
        duplicate an Image

        """
        config = mmc.plugins.imaging.ImagingConfig("imaging")
        newpath = os.path.join(config.publicpath, newname)
        if os.path.exists(newpath): # target already exists
            return 1
        if os.path.islink(newpath): # target already exists
            return 1
        try:
            mmc.plugins.imaging.images.Image(name).copy(newname)
        except: # something weird append
            shutil.rmtree(newpath)
            return 255
        else:   # copy succedeed
            return 0

    def setPublicImageData(name, newname, title, desc):
        """
        duplicate an Image

        """
        config = mmc.plugins.imaging.ImagingConfig("imaging")
        newpath = os.path.join(config.publicpath, newname)
        if name != newname:
            if os.path.exists(newpath): # target already exists
                return 1
            if os.path.islink(newpath): # target already exists
                return 1
            try:
                mmc.plugins.imaging.images.Image(name).move(newname)
            except: # something weird append
                return 255
        mmc.plugins.imaging.images.Image(newname).setTitle(title)
        mmc.plugins.imaging.images.Image(newname).setDesc(desc)
        return 0

    def createIsoFromImage(name, filename, size):
        """
        create an iso from an image

        """
        config = mmc.plugins.imaging.ImagingConfig("imaging")
        image = mmc.plugins.imaging.iso.Iso(name, filename, size)
        image.prepareImage()
        image.createImage()
        return 0

    """ END DEPRECATED """

    ################################################### web def
    def get_web_def_date_fmt(self):
        return xmlrpcCleanup(ImagingConfig().web_def_date_fmt)

    def get_web_def_possible_protocols(self):
        return xmlrpcCleanup(map(lambda p:p.toH(), ImagingDatabase().getAllProtocols()))

    def get_web_def_default_protocol(self):
        return xmlrpcCleanup(ImagingConfig().web_def_default_protocol)

    ###########################################################
    ###### BOOT MENU (image+boot service on the target)
    def __getTargetBootMenu(self, target_id, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        menu = map(lambda l: l.toH(), db.getBootMenu(target_id, start, end, filter))
        count = db.countBootMenu(target_id, filter)
        return [count, xmlrpcCleanup(menu)]

    def getProfileBootMenu(self, target_id, start = 0, end = -1, filter = ''):
        return self.__getTargetBootMenu(target_id, start, end, filter)

    def getComputerBootMenu(self, target_id, start = 0, end = -1, filter = ''):
        return self.__getTargetBootMenu(target_id, start, end, filter)

    def getLocationBootMenu(self, loc_id, start = 0, end = -1, filter = ''):
        # Entities are names Location in the php part, here we convert them from Location to Entity
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getEntityBootMenu(loc_id, start, end, filter))
        count = db.countEntityBootMenu(loc_id, filter)
        return [count, xmlrpcCleanup(ret)]

    # EDITION
    def moveItemUpInMenu(self, target_uuid, type, mi_uuid):
        return ImagingDatabase().moveItemUpInMenu(target_uuid, mi_uuid)

    def moveItemDownInMenu(self, target_uuid, type, mi_uuid):
        return ImagingDatabase().moveItemDownInMenu(target_uuid, mi_uuid)

    def moveItemUpInMenu4Location(self, loc_id, mi_uuid):
        return ImagingDatabase().moveItemUpInMenu4Location(loc_id, mi_uuid)

    def moveItemDownInMenu4Location(self, loc_id, mi_uuid):
        return ImagingDatabase().moveItemDownInMenu4Location(loc_id, mi_uuid)

    ###### IMAGES
    def __getTargetImages(self, id, type, start = 0, end = -1, filter = ''):
        # carrefull the end is used for each list (image and master)
        db = ImagingDatabase()
        reti = map(lambda l: l.toH(), db.getPossibleImages(id, start, end, filter))
        counti = db.countPossibleImages(id, filter)

        retm = map(lambda l: l.toH(), db.getPossibleMasters(id, start, end, filter))
        countm = db.countPossibleMasters(id, filter)

        return {
            'images': [counti, xmlrpcCleanup(reti)],
            'masters': [countm, xmlrpcCleanup(retm)]
        }

    def getComputerImages(self, id, start = 0, end = -1, filter = ''):
        return self.__getTargetImages(id, TYPE_COMPUTER, start, end, filter)

    def getProfileImages(self, id, start = 0, end = -1, filter = ''):
        return self.__getTargetImages(id, TYPE_PROFILE, start, end, filter)

    def getLocationImages(self, loc_id, start = 0, end = -1, filter = ''):
        # Entities are names Location in the php part, here we convert them from Location to Entity
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getEntityMasters(loc_id, start, end, filter))
        count = db.countEntityMasters(loc_id, filter)
        return [count, xmlrpcCleanup(ret)]

    # EDITION
    def addImageToTarget(self, item_uuid, target_uuid, params):
        try:
            ret = ImagingDatabase().addImageToTarget(item_uuid, target_uuid, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            raise e
            return xmlrpcCleanup([False, e])

    def editImageToTarget(self, item_uuid, target_uuid, params):
        try:
            ret = ImagingDatabase().editImageToTarget(item_uuid, target_uuid, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def delImageToTarget(self, item_uuid, target_uuid):
        try:
            ret = ImagingDatabase().delImageToTarget(item_uuid, target_uuid)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def addImageToLocation(self, item_uuid, loc_id, params):
        try:
            ret = ImagingDatabase().addImageToEntity(item_uuid, loc_id, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            raise e
            return xmlrpcCleanup([False, e])

    def editImageToLocation(self, item_uuid, loc_id, params):
        #try:
            ret = ImagingDatabase().editImageToEntity(item_uuid, loc_id, params)
            return xmlrpcCleanup([True, ret])
        #except Exception, e:
        #    return xmlrpcCleanup([False, e])

    def delImageToLocation(self, item_uuid, loc_id):
        try:
            ret = ImagingDatabase().delImageToEntity(item_uuid, loc_id)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    ###### BOOT SERVICES
    def __getTargetBootServices(self, id, type, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getBootServicesOnTargetById(id, start, end, filter))
        count = db.countBootServicesOnTargetById(id, filter)
        return [count, xmlrpcCleanup(ret)]

    def getComputerBootServices(self, id, start = 0, end = -1, filter = ''):
        return self.__getTargetBootServices(id, TYPE_COMPUTER, start, end, filter)

    def getProfileBootServices(self, id, start = 0, end = -1, filter = ''):
        return self.__getTargetBootServices(id, TYPE_PROFILE, start, end, filter)

    def getPossibleBootServices(self, target_uuid, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getPossibleBootServices(target_uuid, start, end, filter))
        count = db.countPossibleBootServices(target_uuid, filter)
        return [count, xmlrpcCleanup(ret)]

    def getLocationBootServices(self, loc_id, start = 0, end = -1, filter = ''):
        # Entities are names Location in the php part, here we convert them from Location to Entity
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getEntityBootServices(loc_id, start, end, filter))
        count = db.countEntityBootServices(loc_id, filter)
        return [count, xmlrpcCleanup(ret)]

    # EDITION
    def addServiceToTarget(self, bs_uuid, target_uuid, params):
        try:
            ret = ImagingDatabase().addServiceToTarget(bs_uuid, target_uuid, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def delServiceToTarget(self, bs_uuid, target_uuid):
        try:
            ret = ImagingDatabase().delServiceToTarget(bs_uuid, target_uuid)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editServiceToTarget(self, bs_uuid, target_uuid, params):
        try:
            ret = ImagingDatabase().editServiceToTarget(bs_uuid, target_uuid, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            raise e
            return xmlrpcCleanup([False, e])

    def addServiceToLocation(self, bs_uuid, location_id, params):
        #try:
            ret = ImagingDatabase().addServiceToEntity(bs_uuid, location_id, params)
            return xmlrpcCleanup([True, ret])
        #except Exception, e:
        #    return xmlrpcCleanup([False, e])

    def delServiceToLocation(self, bs_uuid, location_id):
        #try:
            ret = ImagingDatabase().delServiceToEntity(bs_uuid, location_id)
            return xmlrpcCleanup([True, ret])
        #except Exception, e:
        #    return xmlrpcCleanup([False, e])

    def editServiceToLocation(self, mi_uuid, location_id, params):
        #try:
            ret = ImagingDatabase().editServiceToEntity(mi_uuid, location_id, params)
            return xmlrpcCleanup([True, ret])
        #except Exception, e:
        #    return xmlrpcCleanup([False, e])

    ###### MENU ITEMS
    def getMenuItemByUUID(self, bs_uuid):
        mi = ImagingDatabase().getMenuItemByUUID(bs_uuid)
        if mi != None:
            return xmlrpcCleanup(mi.toH())
        return False

    ###### LOGS
    def __getTargetMasteredOns(self, id, type, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getMasteredOnsOnTargetByIdAndType(id, type, start, end, filter))
        count = db.countMasteredOnsOnTargetByIdAndType(id, type, filter)
        return [count, xmlrpcCleanup(ret)]

    def getComputerLogs(self, id, start = 0, end = -1, filter = ''):
        return self.__getTargetMasteredOns(id, TYPE_COMPUTER, start, end, filter)

    def getProfileLogs(self, id, start = 0, end = -1, filter = ''):
        return self.__getTargetMasteredOns(id, TYPE_PROFILE, start, end, filter)

    def getLogs4Location(self, location_uuid, start = 0, end = -1, filter = ''):
        if location_uuid == False:
            return [0, []]
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getMasteredOns4Location(location_uuid, start, end, filter))
        count = db.countMasteredOns4Location(location_uuid, filter)
        return [count, xmlrpcCleanup(ret)]

    ###### GET IMAGING API URL
    def __chooseImagingApiUrl(self, location):
        db = ImagingDatabase()
        return ImagingDatabase().getEntityUrl(location)

    ###### IMAGING API CALLS
    def getGlobalStatus(self, location):
        url = self.__chooseImagingApiUrl(location)
        i = ImagingApi(url.encode('utf8')) # TODO why do we need to encode....
        # TODO need to be done in async
        if i != None:
            return xmlrpcCleanup(i.imagingServerStatus())
        return {}

    ####### IMAGING SERVER
    def getAllNonLinkedImagingServer(self, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getAllNonLinkedImagingServer(start, end, filter))
        count = db.countAllNonLinkedImagingServer(filter)
        return [count, xmlrpcCleanup(ret)]

    def linkImagingServerToLocation(self, is_uuid, loc_id, loc_name):
        db = ImagingDatabase()
        try:
            ret = db.linkImagingServerToEntity(is_uuid, loc_id, loc_name)
        except Exception, e:
            return [False, str(e)]
        return [True]

    def getImagingServerConfig(self, location):
        imaging_server = ImagingDatabase().getImagingServerByEntityUUID(location)
        default_menu = ImagingDatabase().getEntityDefaultMenu(location)
        if imaging_server and default_menu:
            return xmlrpcCleanup((imaging_server.toH(), default_menu.toH()))
        elif default_menu:
            return [False, ":cant find imaging server linked to location %s"%(location)]
        elif imaging_server:
            return [False, ":cant find the default menu for location %s"%(location), xmlrpcCleanup(imaging_server.toH())]

    def setImagingServerConfig(self, location, config):
        menu = ImagingDatabase().getEntityDefaultMenu(location)
        menu = menu.toH()
        try:
            return xmlrpcCleanup([ImagingDatabase().modifyMenu(menu['imaging_uuid'], config)])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def doesLocationHasImagingServer(self, loc_id):
        return ImagingDatabase().doesLocationHasImagingServer(loc_id)

    ###### REGISTRATION
    def isTargetRegister(self, uuid, type):
        return ImagingDatabase().isTargetRegister(uuid, type)

    def isComputerRegistered(self, machine_uuid):
        return self.isTargetRegister(machine_uuid, TYPE_COMPUTER)

    def isProfileRegistered(self, profile_uuid):
        return self.isTargetRegister(profile_uuid, TYPE_PROFILE)

    ###### Menus
    def getMyMenuTarget(self, uuid, type):
        ret = ImagingDatabase().getMyMenuTarget(uuid, type)
        if ret[1]:
            ret[1] = ret[1].toH()
        return ret

    def setMyMenuTarget(self, uuid, params, type):
        ret = ImagingDatabase().setMyMenuTarget(uuid, params, type)
        return ret

    def getMyMenuComputer(self, uuid):
        return xmlrpcCleanup(self.getMyMenuTarget(uuid, TYPE_COMPUTER))

    def setMyMenuComputer(self, target_uuid, params):
        return xmlrpcCleanup(self.setMyMenuTarget(target_uuid, params, TYPE_COMPUTER))

    def getMyMenuProfile(self, uuid):
        return xmlrpcCleanup(self.getMyMenuTarget(uuid, TYPE_PROFILE))
    
    def setMyMenuProfile(self, target_uuid, params):
        return xmlrpcCleanup(self.setMyMenuTarget(target_uuid, params, TYPE_PROFILE))

    ###### POST INSTALL SCRIPTS
    def getAllPostInstallScripts(self, location, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getAllPostInstallScripts(location, start, end, filter))
        count = db.countAllPostInstallScripts(location, filter)
        return [count, xmlrpcCleanup(ret)]

    def getPostInstallScript(self, pis_uuid):
        pis = ImagingDatabase().getPostInstallScript(pis_uuid)
        if pis:
            return xmlrpcCleanup(pis.toH())
        return xmlrpcCleanup(False)

    # edit
    def delPostInstallScript(self, pis_uuid):
        try:
            return xmlrpcCleanup(ImagingDatabase().delPostInstallScript(pis_uuid))
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editPostInstallScript(self, pis_uuid, params):
        try:
            return xmlrpcCleanup(ImagingDatabase().editPostInstallScript(pis_uuid, params))
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def addPostInstallScript(self, loc_id, params):
        #try:
            return xmlrpcCleanup(ImagingDatabase().addPostInstallScript(loc_id, params))
        #except Exception, e:
        #    return xmlrpcCleanup([False, e])

    ###### API to be called from the imaging server (ie : without authentication)
    def computerRegister(self, hostname, domain, MACAddress, profile, entities):
        """
        Called by the Package Server to register a new computer.
        The computer name may contain a profile and an entity path (like profile:/entityA/entityB/computer)
        """

        computer = {
            'computername'          : hostname, # FIXME : what about domain ?
            'computerdescription'   : '',
            'computerip'            : '',
            'computermac'           : MACAddress,
            'computernet'           : '',
            'location_uuid'         : ''
        }

        ComputerManager().addComputer(None, computer)

        if profile:
            # TODO
            pass


        if entities:
            # TODO
            pass

    def imagingServerRegister(self, name, url, uuid):
        """
        Called by the imagingServer register script, it fills all the required fields for an
        imaging server, then the server is available in the list of server not linked to any entity
        and need to be linked.
        """
        db = ImagingDatabase()
        if db.countImagingServerByPackageServerUUID(uuid) != 0:
            return [False, "The UUID you try to declare (%s) already exists in the database, please check you know what you are doing."%(uuid)]
        db.registerImagingServer(name, url, uuid)
        return [True, "Your Imaging Server has been correctly registered. You can now associate it to the correct entity in the MMC."]

    def getComputerUUID(self, mac):
        """
        Called by the package server, to obtain a computer UUID in exchange of its MAC address
        """
        # TODO, for now return a fake value
        return [True, "FAKE_UUID"]
