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
from mmc.plugins.imaging.config import ImagingConfig
from mmc.support.mmctools import *
from pulse2.database.imaging import ImagingDatabase
from pulse2.database.imaging.types import *
from pulse2.apis.clients.imaging import ImagingApi

VERSION = "0.1"
APIVERSION = "0:0:0"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

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

    ###########################################################
    ###### BOOT MENU (image+boot service on the target)
    def __getTargetBootMenu(self, target_id, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        menu = map(lambda l: l.toH(), db.getBootMenu(target_id, start, end, filter))
        count = db.countBootMenu(target_id, filter)
        return [count, xmlrpcCleanup(menu)]
    
    def getProfileBootMenu(self, target_id, start = 0, end = -1, filter = ''):
        return self.__getTargetBootMenu(target_id, start, end, filter)

    def getMachineBootMenu(self, target_id, start = 0, end = -1, filter = ''):
        return self.__getTargetBootMenu(target_id, start, end, filter)

    def getLocationBootMenu(self, loc_id, start = 0, end = -1, filter = ''):
        # Entities are names Location in the php part, here we convert them from Location to Entity
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getEntityBootMenu(loc_id, start, end, filter))
        count = db.countEntityBootMenu(loc_id, filter)
        return [count, xmlrpcCleanup(ret)]

    # EDITION
    def moveItemUpInMenu(self, target_uuid, type, mi_uuid):
        return ImagingDatabase().moveItemUpInMenu(target_uuid, type, mi_uuid)
        
    def moveItemDownInMenu(self, target_uuid, type, mi_uuid):
        return ImagingDatabase().moveItemDownInMenu(target_uuid, type, mi_uuid)
        
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
    
    def getMachineImages(self, id, start = 0, end = -1, filter = ''):
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

    ###### BOOT SERVICES
    def __getTargetBootServices(self, id, type, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getBootServicesOnTargetById(id, start, end, filter))
        count = db.countBootServicesOnTargetById(id, filter)
        return [count, xmlrpcCleanup(ret)]
        
    def getMachineBootServices(self, id, start = 0, end = -1, filter = ''):
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
        try:
            ret = ImagingDatabase().addServiceToEntity(bs_uuid, location_id, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def delServiceToLocation(self, bs_uuid, location_id):
        try:
            ret = ImagingDatabase().delServiceToEntity(bs_uuid, location_id)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editServiceToLocation(self, bs_uuid, location_id, params):
        try:
            ret = ImagingDatabase().editServiceToEntity(bs_uuid, location_id, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])
        
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
        
    def getMachineLogs(self, id, start = 0, end = -1, filter = ''):
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

   
