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
import shutil
from twisted.internet import defer

import mmc.plugins.imaging.images
import mmc.plugins.imaging.iso
from mmc.support.mmctools import xmlrpcCleanup
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.plugins.imaging.config import ImagingConfig
from mmc.plugins.base.computers import ComputerManager
from pulse2.managers.profile import ComputerProfileManager
from pulse2.managers.location import ComputerLocationManager
from pulse2.database.imaging import ImagingDatabase
from pulse2.database.imaging.types import P2IT, P2ISS, P2IM
from pulse2.apis.clients.imaging import ImagingApi
import pulse2.utils

VERSION = "0.1"
APIVERSION = "0:0:0"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

NOAUTHNEEDED = ['computerRegister',
                'imagingServerRegister',
                'getComputerByMac',
                'imageRegister',
                'logClientAction',
                'injectInventory',
                'getDefaultMenuForSuscription',
                'linkImagingServerToLocation']


def getVersion():
    return VERSION


def getApiVersion():
    return APIVERSION


def getRevision():
    return REVISION


def activate():
    """
    Read the plugin configuration, initialize it, and run some tests to ensure
    it is ready to operate.
    """
    logger = logging.getLogger()
    config = ImagingConfig("imaging")

    if config.disabled:
        logger.warning("Plugin imaging: disabled by configuration.")
        return False

    # Initialize imaging database
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
        image = mmc.plugins.imaging.iso.Iso(name, filename, size)
        image.prepareImage()
        image.createImage()
        return 0

    """ END DEPRECATED """

    ################################################### web def
    def get_web_def_date_fmt(self):
        return xmlrpcCleanup(ImagingConfig().web_def_date_fmt)

    def get_web_def_possible_protocols(self):
        return xmlrpcCleanup(map(lambda p: p.toH(), ImagingDatabase().getAllProtocols()))

    def get_web_def_default_protocol(self):
        return xmlrpcCleanup(ImagingConfig().web_def_default_protocol)

    def get_web_def_kernel_parameters(self):
        return xmlrpcCleanup(ImagingConfig().web_def_kernel_parameters)

    def get_web_def_image_parameters(self):
        return xmlrpcCleanup(ImagingConfig().web_def_image_parameters)

    ###########################################################
    ###### BOOT MENU (image+boot service on the target)
    def __convertType(self, target_type):
        if target_type == '':
            target_type = P2IT.COMPUTER
        elif target_type == 'group':
            target_type = P2IT.PROFILE
        return target_type

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
    def moveItemUpInMenu(self, target_uuid, target_type, mi_uuid):
        db = ImagingDatabase()
        target_type = self.__convertType(target_type)
        db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
        return db.moveItemUpInMenu(target_uuid, mi_uuid)

    def moveItemDownInMenu(self, target_uuid, target_type, mi_uuid):
        db = ImagingDatabase()
        target_type = self.__convertType(target_type)
        db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
        return db.moveItemDownInMenu(target_uuid, mi_uuid)

    def moveItemUpInMenu4Location(self, loc_id, mi_uuid):
        db = ImagingDatabase()
        db.setLocationSynchroState(loc_id, P2ISS.TODO)
        return db.moveItemUpInMenu4Location(loc_id, mi_uuid)

    def moveItemDownInMenu4Location(self, loc_id, mi_uuid):
        db = ImagingDatabase()
        db.setLocationSynchroState(loc_id, P2ISS.TODO)
        return db.moveItemDownInMenu4Location(loc_id, mi_uuid)

    ###### IMAGES
    def __getTargetImages(self, id, target_type, start = 0, end = -1, filter = ''):
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
        return self.__getTargetImages(id, P2IT.COMPUTER, start, end, filter)

    def getProfileImages(self, id, start = 0, end = -1, filter = ''):
        return self.__getTargetImages(id, P2IT.PROFILE, start, end, filter)

    def getLocationImages(self, loc_id, start = 0, end = -1, filter = ''):
        # Entities are names Location in the php part, here we convert them from Location to Entity
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getEntityMasters(loc_id, start, end, filter))
        count = db.countEntityMasters(loc_id, filter)
        return [count, xmlrpcCleanup(ret)]

    # EDITION
    def addImageToTarget(self, item_uuid, target_uuid, params, target_type):
        db = ImagingDatabase()
        target_type = self.__convertType(target_type)
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = db.addImageToTarget(item_uuid, target_uuid, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            raise e
            return xmlrpcCleanup([False, e])

    def editImageToTarget(self, item_uuid, target_uuid, params, target_type):
        db = ImagingDatabase()
        target_type = self.__convertType(target_type)
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = db.editImageToTarget(item_uuid, target_uuid, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editImage(self, item_uuid, target_uuid, params, target_type):
        db = ImagingDatabase()
        target_type = self.__convertType(target_type)
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = db.editImage(item_uuid, target_uuid, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            raise e
            return xmlrpcCleanup([False, e])

    def delImageToTarget(self, item_uuid, target_uuid, target_type):
        db = ImagingDatabase()
        target_type = self.__convertType(target_type)
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = db.delImageToTarget(item_uuid, target_uuid)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def addImageToLocation(self, item_uuid, loc_id, params):
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(loc_id, P2ISS.TODO)
            ret = db.addImageToEntity(item_uuid, loc_id, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            raise e
            return xmlrpcCleanup([False, e])

    def editImageToLocation(self, item_uuid, loc_id, params):
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(loc_id, P2ISS.TODO)
            ret = db.editImageToEntity(item_uuid, loc_id, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def delImageToLocation(self, item_uuid, loc_id):
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(loc_id, P2ISS.TODO)
            ret = db.delImageToEntity(item_uuid, loc_id)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    ###### BOOT SERVICES
    def __getTargetBootServices(self, id, target_type, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getBootServicesOnTargetById(id, start, end, filter))
        count = db.countBootServicesOnTargetById(id, filter)
        return [count, xmlrpcCleanup(ret)]

    def getComputerBootServices(self, id, start = 0, end = -1, filter = ''):
        return self.__getTargetBootServices(id, P2IT.COMPUTER, start, end, filter)

    def getProfileBootServices(self, id, start = 0, end = -1, filter = ''):
        return self.__getTargetBootServices(id, P2IT.PROFILE, start, end, filter)

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
    def addServiceToTarget(self, bs_uuid, target_uuid, params, target_type):
        db = ImagingDatabase()
        if target_type == '':
            target_type = P2IT.COMPUTER
        elif target_type == 'group':
            target_type = P2IT.PROFILE
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = ImagingDatabase().addServiceToTarget(bs_uuid, target_uuid, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def delServiceToTarget(self, bs_uuid, target_uuid, target_type):
        db = ImagingDatabase()
        if target_type == '':
            target_type = P2IT.COMPUTER
        elif target_type == 'group':
            target_type = P2IT.PROFILE
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = ImagingDatabase().delServiceToTarget(bs_uuid, target_uuid)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editServiceToTarget(self, bs_uuid, target_uuid, params, target_type):
        db = ImagingDatabase()
        if target_type == '':
            target_type = P2IT.COMPUTER
        elif target_type == 'group':
            target_type = P2IT.PROFILE
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = ImagingDatabase().editServiceToTarget(bs_uuid, target_uuid, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            raise e
            return xmlrpcCleanup([False, e])

    def addServiceToLocation(self, bs_uuid, location_id, params):
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(location_id, P2ISS.TODO)
            ret = ImagingDatabase().addServiceToEntity(bs_uuid, location_id, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def delServiceToLocation(self, bs_uuid, location_id):
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(location_id, P2ISS.TODO)
            ret = ImagingDatabase().delServiceToEntity(bs_uuid, location_id)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editServiceToLocation(self, mi_uuid, location_id, params):
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(location_id, P2ISS.TODO)
            ret = ImagingDatabase().editServiceToEntity(mi_uuid, location_id, params)
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
    def __getTargetMasteredOns(self, id, target_type, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getMasteredOnsOnTargetByIdAndType(id, target_type, start, end, filter))
        count = db.countMasteredOnsOnTargetByIdAndType(id, target_type, filter)
        return [count, xmlrpcCleanup(ret)]

    def getComputerLogs(self, id, start = 0, end = -1, filter = ''):
        return self.__getTargetMasteredOns(id, P2IT.COMPUTER, start, end, filter)

    def getProfileLogs(self, id, start = 0, end = -1, filter = ''):
        return self.__getTargetMasteredOns(id, P2IT.PROFILE, start, end, filter)

    def getLogs4Location(self, location_uuid, start = 0, end = -1, filter = ''):
        if location_uuid == False:
            return [0, []]
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getMasteredOns4Location(location_uuid, start, end, filter))
        count = db.countMasteredOns4Location(location_uuid, filter)
        return [count, xmlrpcCleanup(ret)]

    ###### GET IMAGING API URL
    def __chooseImagingApiUrl(self, location):
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
            db.linkImagingServerToEntity(is_uuid, loc_id, loc_name) # FIXME : are not we supposed to deal with the return value ?
            db.setLocationSynchroState(loc_id, P2ISS.TODO)
        except Exception, e:
            logging.getLogger().warn("Imaging.linkImagingServerToLocation : %s" % e)
            return [False, "Failed to link Imaging Server to Location : %s" % e]
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
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(location, P2ISS.TODO)
            return xmlrpcCleanup([db.modifyMenu(menu['imaging_uuid'], config)])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def doesLocationHasImagingServer(self, loc_id):
        return ImagingDatabase().doesLocationHasImagingServer(loc_id)

    ###### REGISTRATION
    def isTargetRegister(self, uuid, target_type):
        return ImagingDatabase().isTargetRegister(uuid, target_type)

    def isComputerRegistered(self, machine_uuid):
        return self.isTargetRegister(machine_uuid, P2IT.COMPUTER)

    def isProfileRegistered(self, profile_uuid):
        return self.isTargetRegister(profile_uuid, P2IT.PROFILE)

    ###### Synchronisation
    def getTargetSynchroState(self, uuid, target_type):
        ret = ImagingDatabase().getTargetsSynchroState([uuid], target_type)
        return ret[0]

    def getComputerSynchroState(self, uuid):
        if not self.isTargetRegister(uuid, P2IT.COMPUTER):
            return {'id':0}
        ret = self.getTargetSynchroState(uuid, P2IT.COMPUTER)
        return xmlrpcCleanup(ret.toH())

    def getProfileSynchroState(self, uuid):
        if not self.isTargetRegister(uuid, P2IT.PROFILE):
            return {'id':0}
        ret = self.getTargetSynchroState(uuid, P2IT.PROFILE)
        return xmlrpcCleanup(ret.toH())

    def getLocationSynchroState(self, uuid):
        if not self.doesLocationHasImagingServer(uuid):
            return {'id':0}
        ret = ImagingDatabase().getLocationSynchroState(uuid)
        if type(ret) != dict:
            ret = ret.toH()
        return xmlrpcCleanup(ret)

    def __generateMenusContent(self, menu, menu_items, loc_uuid, target_uuid = None, h_pis = {}):
        menu['bootservices'] = {}
        menu['images'] = {}
        for mi in menu_items:
            if menu['fk_default_item'] == mi.id:
                menu['default_item'] = mi.order
            if menu['fk_default_item_WOL'] == mi.id:
                menu['default_item_WOL'] = mi.order
                menu['default_item_wol'] = mi.order # TODO : remove
            mi = mi.toH()
            if mi.has_key('image'):
                if h_pis.has_key(mi['image']['id']):
                    h_pis[mi['image']['id']].append([loc_uuid, target_uuid, str(mi['order'])])
                else:
                    h_pis[mi['image']['id']] = [[loc_uuid, target_uuid, str(mi['order'])]]
                im = {
                    'uuid' : mi['image']['uuid'],
                    'name' : mi['image']['name'],
                    'desc' : mi['image']['desc']
                }
                menu['images'][str(mi['order'])] = im
            else:
                bs = {
                    'name' : mi['boot_service']['default_name'],
                    'desc' : mi['boot_service']['default_desc'],
                    'value' : mi['boot_service']['value'],
                    'hidden' : mi['hidden'],
                    'hidden_WOL' : mi['hidden_WOL']
                }
                menu['bootservices'][str(mi['order'])] = bs
        return (menu, menu_items, h_pis)

    def __generateDefaultSuscribeMenu(self, logger, db):
        menu = db.getDefaultSuscribeMenu()
        menu_items = db.getMenuContent(menu.id, P2IM.ALL, 0, -1, '')
        menu = menu.toH()
        menu, menu_items, h_pis = self.__generateMenusContent(menu, menu_items, None)
        ims = h_pis.keys()
        a_pis = db.getImagesPostInstallScript(ims)
        for pis, im in a_pis:
            pis = {
                'id':pis.id,
                'name':pis.default_name,
                'desc':pis.default_desc,
                'value':pis.value
            }
            a_targets = h_pis[im.id]
            for loc_uuid, t_uuid, order in a_targets:
                # loc_uuid = None
                # t_uuid = None
                menu['images'][order]['post_install_script'] = pis
        return menu

    def __generateLocationMenu(self, logger, db, loc_uuid):
        menu = db.getEntityDefaultMenu(loc_uuid)
        menu_items = db.getMenuContent(menu.id, P2IM.ALL, 0, -1, '')
        menu = menu.toH()
        menu, menu_items, h_pis = self.__generateMenusContent(menu, menu_items, loc_uuid)
        ims = h_pis.keys()
        a_pis = db.getImagesPostInstallScript(ims)
        for pis, im in a_pis:
            pis = {
                'id':pis.id,
                'name':pis.default_name,
                'desc':pis.default_desc,
                'value':pis.value
            }
            a_targets = h_pis[im.id]
            for loc_uuid, t_uuid, order in a_targets:
                menu['images'][order]['post_install_script'] = pis
        return menu

    def __generateMenus(self, logger, db, uuids, target_type):
        # get target location
        locations = ComputerLocationManager().getMachinesLocations(uuids)
        if len(locations.keys()) != len(uuids):
            # do fail
            logger.error("couldn't get the target entity for %s"%(str(uuids)))
        distinct_loc = {}
        h_pis = {}

        targets = db.getTargetsByUUID(uuids)
        h_targets = {}
        for target in targets:
            h_targets[target.uuid] = target.toH()

        for m_uuid in locations:
            loc_uuid = "UUID%s"%locations[m_uuid]['id']
            menu_items = db.getBootMenu(m_uuid, 0, -1, '')
            menu = db.getTargetsMenuTUUID(m_uuid)
            menu = menu.toH()
            menu['target'] = h_targets[m_uuid]
            menu, menu_items, h_pis = self.__generateMenusContent(menu, menu_items, loc_uuid, m_uuid, h_pis)

            if distinct_loc.has_key(loc_uuid):
                distinct_loc[loc_uuid][1][m_uuid] = menu
            else:
                url = self.__chooseImagingApiUrl(loc_uuid)
                distinct_loc[loc_uuid] = [url, {m_uuid:menu}]

        ims = h_pis.keys()
        a_pis = db.getImagesPostInstallScript(ims)
        for pis, im in a_pis:
            pis = {
                'id':pis.id,
                'name':pis.default_name,
                'desc':pis.default_desc,
                'value':pis.value
            }
            a_targets = h_pis[im.id]
            for loc_uuid, t_uuid, order in a_targets:
                distinct_loc[loc_uuid][1][t_uuid]['images'][order]['post_install_script'] = pis
        return distinct_loc

    def __synchroLocation(self, loc_uuid):
        logger = logging.getLogger()
        db = ImagingDatabase()
        ret = db.setLocationSynchroState(loc_uuid, P2ISS.RUNNING)
        menu = self.__generateLocationMenu(logger, db, loc_uuid)
        def treatFailures(result, location_uuid = loc_uuid, menu = menu, logger = logger):
            if result:
                db.setLocationSynchroState(loc_uuid, P2ISS.DONE)
            else:
                db.setLocationSynchroState(loc_uuid, P2ISS.TODO)
            return result

        url = self.__chooseImagingApiUrl(loc_uuid)
        i = ImagingApi(url.encode('utf8')) # TODO why do we need to encode....
        if i == None:
            # do fail
            logger.error("couldn't initialize the ImagingApi to %s"%(url))
        d = i.imagingServerDefaultMenuSet(menu) # WIP
        d.addCallback(treatFailures)
        return d

    def __synchroTargets(self, uuids, target_type):
        logger = logging.getLogger()
        db = ImagingDatabase()
        ret = db.changeTargetsSynchroState(uuids, target_type, P2ISS.RUNNING)
        distinct_loc = self.__generateMenus(logger, db, uuids, target_type)

        def treatFailures(result, location_uuid, distinct_loc = distinct_loc, logger = logger, target_type = target_type):
            failures = []
            success = []
            for fuuid in result:
                logger.warn("failed to synchronize menu for %s"%(str(fuuid)))
                failures.append(fuuid)
                # failure menu distinct_loc[location_uuid][1][fuuid]

            for uuid in distinct_loc[location_uuid][1]:
                if not uuid in failures:
                    logger.debug("succeed to synchronize menu for %s"%(str(uuid)))
                    success.append(uuid)
            db.changeTargetsSynchroState(failures, target_type, P2ISS.TODO)
            db.changeTargetsSynchroState(success, target_type, P2ISS.DONE)
            return failures

        dl = []
        for location_uuid in distinct_loc:
            url = distinct_loc[location_uuid][0]
            i = ImagingApi(url.encode('utf8')) # TODO why do we need to encode....
            if i == None:
                # do fail
                logger.error("couldn't initialize the ImagingApi to %s"%(url))

            l_menus = distinct_loc[location_uuid][1]
            print "WOOT : %s" % l_menus
            d = i.computersMenuSet(l_menus)
            d.addCallback(treatFailures, location_uuid)
            dl.append(d)

        def sendResult(results):
            failures = []
            for s, uuids in results:
                failures.extend(uuids)
            if len(failures) == 0:
                return [True]
            return [False, failures]

        dl = defer.DeferredList(dl)
        dl.addCallback(sendResult)
        return dl

    def synchroComputer(self, uuid):
        if not self.isTargetRegister(uuid, P2IT.COMPUTER):
            return False
        ret = self.__synchroTargets([uuid], P2IT.COMPUTER)
        return xmlrpcCleanup(ret)

    def synchroProfile(self, uuid):
        if not self.isTargetRegister(uuid, P2IT.PROFILE):
            return False
        ret = self.__synchroTargets([uuid], P2IT.PROFILE)
        return xmlrpcCleanup(ret)

    def synchroLocation(self, uuid):
        db = ImagingDatabase()
        # get computers in location that need synchro
        uuids = db.getComputersThatNeedSynchroInEntity(uuid)
        def __getUUID(x):
            x = x[0].toH()
            return x['uuid']
        uuids = map(__getUUID, uuids)
        # get computers in profiles of location that need synchro
        pids = db.getProfilesThatNeedSynchroInEntity(uuid)
        puuids = []
        for profile, synchro_state in pids:
            pid = profile.uuid
            puuids.extend(map(lambda c: c.uuid, ComputerProfileManager().getProfileContent(pid)))
        puuids = db.getComputersSynchroStates(puuids)
        pids_uuids = []
        for computer, synchro_state in puuids:
            if synchro_state.id == P2ISS.TODO or synchro_state.id == P2ISS.INIT_ERROR:
                computer = computer.toH()
                pids_uuids.append(computer['uuid'])

        uuids.extend(pids_uuids)
        # synchronize all
        # ret1 = self.__synchroTargets(uuids, P2IT.COMPUTER)
        # synchro the location
        ret2 = self.__synchroLocation(uuid)
        return ret2

#        def sendResult(results):
#            return xmlrpcCleanup(results)
#
#        dl = defer.DeferredList((ret1, ret2))
#        dl.addCallback(sendResult)
#        return dl

    ###### Menus
    def getMyMenuTarget(self, uuid, target_type):
        ret = ImagingDatabase().getMyMenuTarget(uuid, target_type)
        if ret[1]:
            ret[1] = ret[1].toH()
        return ret

    def setMyMenuTarget(self, uuid, params, target_type):
        db = ImagingDatabase()
        isRegistered = db.isTargetRegister(uuid, target_type)
        try:
            ret = db.setMyMenuTarget(uuid, params, target_type)
        except Exception, e:
            return [False, e]

        #WIP
        if not isRegistered:
            logger = logging.getLogger()
            db = ImagingDatabase()
            ret = db.changeTargetsSynchroState([uuid], target_type, P2ISS.RUNNING)
            distinct_loc = self.__generateMenus(logger, db, [uuid], target_type)

            if target_type == P2IT.COMPUTER:
                location = db.getTargetsEntity([uuid])[0]
                url = self.__chooseImagingApiUrl(location[0].uuid)
                i = ImagingApi(url.encode('utf8')) # TODO why do we need to encode....
                if i != None:
                    # imagingData = {'uuid':uuid}
                    menu = distinct_loc[location[0].uuid][1]
                    imagingData = {'menu':menu, 'uuid':uuid}
                    ctx = self.currentContext
                    MACAddress = ComputerManager().getMachineMac(ctx, {'uuid':uuid})
                    def treatRegister(result, location = location, uuid = uuid):
                        if result:
                            db.changeTargetsSynchroState([uuid], target_type, P2ISS.DONE)
                            return [True]
                        else:
                            # revert the target registering!
                            db.changeTargetsSynchroState([uuid], target_type, P2ISS.INIT_ERROR)
                            return [False, 'P2ISS.INIT_ERROR']

                    d = i.computerRegister(params['target_name'], MACAddress[0], imagingData)
                    d.addCallback(treatRegister)
                    return d
                else:
                    logger.error("couldn't initialize the ImagingApi to %s"%(url))
                    return [False, ""]
            else:
                pass
                #locations = db.getTargetsEntity([uuid])

        return [True]

    def getMyMenuComputer(self, uuid):
        return xmlrpcCleanup(self.getMyMenuTarget(uuid, P2IT.COMPUTER))

    def setMyMenuComputer(self, target_uuid, params):
        return xmlrpcCleanup(self.setMyMenuTarget(target_uuid, params, P2IT.COMPUTER))

    def getMyMenuProfile(self, uuid):
        return xmlrpcCleanup(self.getMyMenuTarget(uuid, P2IT.PROFILE))

    def setMyMenuProfile(self, target_uuid, params):
        return xmlrpcCleanup(self.setMyMenuTarget(target_uuid, params, P2IT.PROFILE))

    ###### POST INSTALL SCRIPTS
    def getAllTargetPostInstallScript(self, target_uuid, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getAllTargetPostInstallScript(target_uuid, start, end, filter))
        count = db.countAllTargetPostInstallScript(target_uuid, filter)
        return [count, xmlrpcCleanup(ret)]

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
        # TODO should be sync
        try:
            return xmlrpcCleanup(ImagingDatabase().delPostInstallScript(pis_uuid))
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editPostInstallScript(self, pis_uuid, params):
        # TODO should be sync
        try:
            return xmlrpcCleanup(ImagingDatabase().editPostInstallScript(pis_uuid, params))
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def addPostInstallScript(self, loc_id, params):
        # TODO should be sync
        try:
            return xmlrpcCleanup(ImagingDatabase().addPostInstallScript(loc_id, params))
        except Exception, e:
            return xmlrpcCleanup([False, e])

    ###### API to be called from the imaging server (ie : without authentication)
    def computerRegister(self, imaging_server_uuid, hostname, domain, MACAddress, profile, entity = None):
        """
        Called by the Package Server to register a new computer.
        The computer name may contain a profile and an entity path (like profile:/entityA/entityB/computer)
        """

        logger = logging.getLogger()
        db = ImagingDatabase()

        imaging_server = db.getImagingServerByPackageServerUUID(imaging_server_uuid, True)
        if not imaging_server:
            return [False, "Failed to find the imaging server %s" % imaging_server_uuid]
        imaging_server = imaging_server[0]
        if imaging_server == None:
            return [False, "Failed to find the imaging server %s" % imaging_server_uuid]

        loc_id = imaging_server[1].uuid
        print imaging_server[1]
        computer = {
            'computername': hostname, # FIXME : what about domain ?
            'computerdescription': '',
            'computerip': '',
            'computermac': MACAddress,
            'computernet': '',
            'location_uuid': loc_id}

        uuid = None
        db_computer = ComputerManager().getComputerByMac(MACAddress)
        if db_computer != None:
            uuid = db_computer['uuid']
        if uuid == None or type(uuid) == list and len(uuid) == 0:
            logger.info("the computer %s (%s) does not exist in the backend, trying to add it" % (hostname, MACAddress))
            # the computer does not exists, so we create it
            uuid = ComputerManager().addComputer(None, computer)
            if uuid == None:
                logger.error("failed to create computer %s (%s)" % (hostname, MACAddress))
                return [False, "failed to create computer %s (%s)" % (hostname, MACAddress)]
            else:
                logger.debug("The computer %s (%s) has been successfully added to the inventory database" % (hostname, MACAddress))
        else:
            logger.debug("computer %s (%s) already exists, we dont need to declare it again" % (hostname, MACAddress))

        target_type = P2IT.COMPUTER
        if not db.isTargetRegister(uuid, target_type):
            logger.info("computer %s (%s) needs to be registered" % (hostname, MACAddress))
            params = {
                'target_name': hostname,
            }
            # Set the computer menu
            db.setMyMenuTarget(uuid, params, target_type) # FIXME : are not we supposed to deal with the return value ?
            # Tell the MMC agent to synchronize the menu
            # As it in some way returns a deferred object, it is run in
            # background
            self.synchroComputer(uuid)
        else:
            logger.debug("computer %s (%s) dont need registration" % (hostname, MACAddress))

        if profile:
            # TODO
            pass

#        if entities:
#            # TODO
#            pass
        return [True, uuid]

    def imagingServerRegister(self, name, url, uuid):
        """
        Called by the imagingServer register script, it fills all the required fields for an
        imaging server, then the server is available in the list of server not linked to any entity
        and need to be linked.
        """
        db = ImagingDatabase()
        if db.countImagingServerByPackageServerUUID(uuid) != 0:
            return [False, "The UUID you try to declare (%s) already exists in the database, please check you know what you are doing." % (uuid)]
        db.registerImagingServer(name, url, uuid)
        return [True, "Your Imaging Server has been correctly registered. You can now associate it to the correct entity in the MMC."]

    def getComputerByMac(self, mac):
        """
        Called by the package server, to obtain a computer UUID/shortname/fqdn in exchange of its MAC address
        """
        assert pulse2.utils.isMACAddress(mac)
        computer = ComputerManager().getComputerByMac(mac)
        if not computer:
            return [False, "imaging.getComputerByMac() : I was unable to find a computer corresponding to the MAC address %s" % mac]
        return [True, {'uuid': "UUID%s" % computer['uuid'], 'mac': mac, 'shortname': computer['hostname'], 'fqdn': computer['hostname']}]

    def logClientAction(self, uuid, level, phase, message):
        """
        Called by the package server, to log some info
        """
        # TODO !!!
        return [True, True]

    def imageRegister(self, imaging_server_uuid, computer_uuid, image_uuid, is_master, name, desc, path, size, creation_date, creator='root'):
        """
        Called by the Package Server to register a new Image.
        """
        image = {
            'name': name,
            'desc': desc,
            'path': path,
            'uuid': image_uuid,
            'checksum': '',
            'size': size,
            'creation_date': creation_date,
            'is_master': is_master,
            'creator': creator}
        db = ImagingDatabase()
        if db.countImagingServerByPackageServerUUID(imaging_server_uuid) == 0:
            return [False, "The imaging server UUID you try to access doesn't exist in the imaging database."]
        if not db.isTargetRegister(computer_uuid, P2IT.COMPUTER):
            return [False, "The computer UUID you try to access doesn't exists in the imaging database."]

        try:
            ret = db.registerImage(imaging_server_uuid, computer_uuid, image)
            ret = [ret, '']
        except Exception, e:
            self.logger.exception(e)
            ret = [False, str(e)]
        return ret

    def injectInventory(self, computer_uuid, inventory=None):
        """
        Called by the Package Server to inject an inventory.
        """
        # TODO !
        return [True, True]

    def getDefaultMenuForSuscription(self):
        """
        Called by the Package Server to get the default menu used by computers to suscribe from the database.
        """
        db = ImagingDatabase()
        logger = logging.getLogger()
        menu = self.__generateDefaultSuscribeMenu(logger, db)
        return xmlrpcCleanup(menu)
