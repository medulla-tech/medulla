# -*- coding:Utf-8; -*-
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
from twisted.internet import defer
from sets import Set as set
import time, ipaddr
import traceback
from mmc.support.mmctools import xmlrpcCleanup
from mmc.support.mmctools import RpcProxyI #, ContextMakerI, SecurityContext
from mmc.core.tasks import TaskManager
from mmc.plugins.imaging.config import ImagingConfig
from mmc.plugins.base.computers import ComputerManager
from pulse2.managers.profile import ComputerProfileManager
from pulse2.managers.location import ComputerLocationManager
from pulse2.managers.pulse import Pulse2Manager
from pulse2.database.imaging import ImagingDatabase, NoImagingServerError
from pulse2.database.imaging.types import P2IT, P2ISS, P2IM, P2ERR
from pulse2.apis.clients.imaging import ImagingApi
import pulse2.utils
import threading
from os import path, makedirs, listdir, remove, rename
import subprocess
import json
import hashlib
import socket

def is_ipv4_valid(ip_string):
    try:
        socket.inet_aton(ip_string)
    except socket.error as e:
        return False
    return True

def fromUUID(uuid):
    return int(uuid.replace('UUID', ''))

def toUUID(id):
    return "UUID%s" % (str(id))

def md5file(fname):
     hash = hashlib.md5()
     with open(fname, "rb") as f:
         for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
     return hash.hexdigest()

class ImagingRpcProxy(RpcProxyI):
    checkThread = {} # check thread actif waitting transfert
    checkThreadData={} # check thread transfert

    def getGeneratedMenu(self, mac):
        # uuid
        logger = logging.getLogger()
        db_computer = ComputerManager().getComputerByMac(mac)
        uuid = 'UUID' + str(db_computer.id)
        menu = generateMenus(logger, ImagingDatabase(), [uuid], unique=True)
        return xmlrpcCleanup(menu)

    def check_process(self, process):
        return xmlrpcCleanup(pulse2.utils.check_process(process))

    """ XML/RPC Bindings """
    ################################################### web def
    """ Functions to access the web default values as defined in the configuration """
    def get_web_def_date_fmt(self):
        """ get the date format """
        return xmlrpcCleanup(ImagingConfig().web_def_date_fmt)

    def get_web_def_kernel_parameters(self):
        """ get the default kernel parameters """
        return xmlrpcCleanup(ImagingConfig().web_def_kernel_parameters)

    def get_web_def_image_parameters(self):
        """ get the default image backup and restoration parameters """
        return xmlrpcCleanup(ImagingConfig().web_def_image_parameters)

    def get_web_def_image_hidden(self):
        """ get the default "Displayed" value when we add an image to a computer """
        return xmlrpcCleanup(ImagingConfig().web_def_image_hidden)

    def get_web_def_image_hidden_WOL(self):
        """ get the default "Displayed on WOL" value when we add an image to a computer """
        return xmlrpcCleanup(ImagingConfig().web_def_image_hidden_wol)

    def get_web_def_image_default(self):
        """ get the default "Selected by default" value when we add an image to a computer """
        return xmlrpcCleanup(ImagingConfig().web_def_image_default)

    def get_web_def_image_default_WOL(self):
        """ get the default "Selected by default on WOL" value when we add an image to a computer """
        return xmlrpcCleanup(ImagingConfig().web_def_image_default_wol)

    def get_web_def_service_hidden(self):
        """ get the default "Displayed" value when we add an service to a computer """
        return xmlrpcCleanup(ImagingConfig().web_def_service_hidden)

    def get_web_def_service_hidden_WOL(self):
        """ get the default "Displayed on WOL" value when we add an service to a computer """
        return xmlrpcCleanup(ImagingConfig().web_def_service_hidden_wol)

    def get_web_def_service_default(self):
        """ get the default "Selected by default" value when we add an service to a computer """
        return xmlrpcCleanup(ImagingConfig().web_def_service_default)

    def get_web_def_service_default_WOL(self):
        """ get the default "Selected by default on WOL" value when we add an service to a computer """
        return xmlrpcCleanup(ImagingConfig().web_def_service_default_wol)

    ###########################################################
    def get_all_known_languages(self):
        """ get all the languages defined in the database """
        return xmlrpcCleanup(map(lambda p: p.toH(), ImagingDatabase().getAllKnownLanguages()))

    ###########################################################
    ###### BOOT MENU (image+boot service on the target)
    def __convertType(self, target_type, target_id):
        """ convert type from '' or 'group' to P2IT.COMPUTER and P2IT.PROFILE """
        if target_type == '':
            profile = ComputerProfileManager().getComputersProfile(target_id)
            if profile != None:
                target_type = P2IT.COMPUTER_IN_PROFILE
            else:
                target_type = P2IT.COMPUTER
        elif target_type == 'group':
            target_type = P2IT.PROFILE
        return target_type

    def __getTargetBootMenu(self, target_id, type, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        menu = map(lambda l: l.toH(), db.getBootMenu(target_id, type, start, end, filter))
        count = db.countBootMenu(target_id, type, filter)
        return [count, xmlrpcCleanup(menu)]

    def hasMoreThanOneEthCard(self, uuids):
        ctx = self.currentContext
        return hasMoreThanOneEthCard(ctx, uuids)

    def getProfileBootMenu(self, target_id, start = 0, end = -1, filter = ''):
        """
        get a profile boot menu

        @param target_id: the uuid of the profile (field Target.uuid)
        @type target_id: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        return self.__getTargetBootMenu(target_id, P2IT.PROFILE, start, end, filter)

    def getComputerBootMenu(self, target_id, start = 0, end = -1, filter = ''):
        """
        get a computer boot menu

        @param target_id: the uuid of the profile (field Target.uuid)
        @type target_id: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        return self.__getTargetBootMenu(target_id, P2IT.COMPUTER, start, end, filter)


    def getTargetsByCustomMenuInEntity(self,loc_uuid, custom_menu):
        """
        get enity computer list that have a given custom_menu flag

        @param loc_uuid: the uuid of the entity
        @type loc_uuid: str

        @param custom_menu: the beginning of the list, default 0
        @type custom_menu: int or str

        @returns: return computers uuid list
        @rtype: list
        """
        return ImagingDatabase().getTargetsByCustomMenuInEntity(loc_uuid, custom_menu)

    def resetComputerBootMenu(self, uuid):
        """
        restore default location boot menu for a host

        @param uuid: the uuid of the computer
        @type uuid: str

        @returns: True if succeeds
        @rtype: bool
        """
        old_bootMenu = self.getComputerBootMenu(uuid)
        # Adding location default menu entries
        # get computer location
        try:
            entity_uuid = ComputerLocationManager().getMachinesLocations([uuid])[uuid]['uuid']
        except KeyError:
            raise Exception("Unable to generate menu for computer %s: deleted but still present in imaging database" % uuid)
        # get location bootMenu
        locationBM = self.getLocationBootMenu(entity_uuid)
        #return locationBM
        for entry in locationBM[1]:
            params = {}
            params['default'] = entry['default']
            params['default_WOL'] = entry['default_WOL']
            params['hidden'] = entry['hidden']
            params['hidden_WOL'] = entry['hidden_WOL']
            if 'boot_service' in entry:
                params['name'] = entry['boot_service']['default_name']
                self.addServiceToTarget(entry['boot_service']['db_uuid'] , uuid, params, '')
            elif 'image' in entry:
                params['name'] = entry['image']['name']
                self.addImageToTarget(entry['image']['db_uuid'], uuid, params, '')
        #

        # Clear old bootMenu entries
        for entry in old_bootMenu[1]:
            if 'boot_service' in entry:
                # It's a boot service
                self.delServiceToTarget(entry['boot_service']['db_uuid'],uuid,'')
            elif 'image' in entry:
                # It's an image
                self.delImageToTarget(entry['image']['db_uuid'],uuid,'')

        # Reset custom_menu flag
        self.setComputerCustomMenuFlag(uuid, 0)

        # Synchronize Boot menu with imaging server
        self.synchroComputer(uuid)
        return True


    def applyLocationDefaultBootMenu(self, loc_uuid, immediate = False):
        """
        apply location boot menu to all location machines that have
        no custom menu

        @param loc_uuid: the uuid of the location
        @type loc_uuid: str

        @returns: return a list with result status
        @rtype: list
        """
        def _applyLocationDefaultBootMenu(loc_uuid):
            try:
                # Get all machine that have not a custom_menu
                logging.getLogger().info('Applying default location BootMenu [%s]', loc_uuid)
                for uuid in self.getTargetsByCustomMenuInEntity(loc_uuid, 0):
                    try:
                        self.resetComputerBootMenu(uuid)
                    except Exception, e:
                        logging.getLogger().error(str(e))
            except Exception, e:
                logging.getLogger().error('Unable to apply location default bootmenu')
                logging.getLogger().error(e)

        if not immediate:
            TaskManager().addTask('imaging.applyLocationDefaultBootMenu', (_applyLocationDefaultBootMenu, [loc_uuid]), delay=30)
        else:
            _applyLocationDefaultBootMenu(loc_uuid)
        return [True]

    def SynchroAllLocationComputers(self, loc_uuid):
        try:
            computers = ImagingDatabase().getRegisteredComputersForEntity(loc_uuid)
            for computer in computers:
                self.synchroComputer(computer)
            return True
        except Exception, e:
            logging.getLogger().error(str(e))
            return False


    def getLocationBootMenu(self, loc_id, start = 0, end = -1, filter = ''):
        """
        get a location boot menu

        @param loc_id: the uuid of the location (field Entity.uuid)
        @type loc_id: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        # Entities are names Location in the php part, here we convert them from Location to Entity
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getEntityBootMenu(loc_id, start, end, filter))
        count = db.countEntityBootMenu(loc_id, filter)
        return [count, xmlrpcCleanup(ret)]

    # EDITION
    def moveItemUpInMenu(self, target_uuid, target_type, mi_uuid):
        """
        move a menu item up in the target's boot menu

        @param target_uuid: the uuid of the target (field Target.uuid)
        @type target_uuid: str

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @param mi_uuid: the menu item to move UUID
        @type mi_uuid: str

        @returns: True if succeed to move the menu item, else return False
        @rtype: boolean
        """
        db = ImagingDatabase()
        target_type = self.__convertType(target_type, target_uuid)
        db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
        # Set custom menu flag to 1
        if target_type == P2IT.COMPUTER:
            self.setComputerCustomMenuFlag(target_uuid,1)
        return db.moveItemUpInMenu(target_uuid, mi_uuid)

    def moveItemDownInMenu(self, target_uuid, target_type, mi_uuid):
        """
        move a menu item down in the target's boot menu

        @param target_uuid: the uuid of the target (field Target.uuid)
        @type target_uuid: str

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @param mi_uuid: the menu item to move UUID
        @type mi_uuid: str

        @returns: True if succeed to move the menu item, else return False
        @rtype: boolean
        """
        db = ImagingDatabase()
        target_type = self.__convertType(target_type, target_uuid)
        db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
        # Set custom menu flag to 1
        if target_type == P2IT.COMPUTER:
            self.setComputerCustomMenuFlag(target_uuid,1)
        return db.moveItemDownInMenu(target_uuid, mi_uuid)

    def moveItemUpInMenu4Location(self, loc_id, mi_uuid):
        """
        move a menu item up in the location boot menu

        @param target_uuid: the uuid of the location (field Entity.uuid)
        @type target_uuid: str

        @param mi_uuid: the menu item to move UUID
        @type mi_uuid: str

        @returns: True if succeed to move the menu item, else return False
        @rtype: boolean
        """
        db = ImagingDatabase()
        db.setLocationSynchroState(loc_id, P2ISS.TODO)
        return db.moveItemUpInMenu4Location(loc_id, mi_uuid)

    def moveItemDownInMenu4Location(self, loc_id, mi_uuid):
        """
        move a menu item down in the location boot menu

        @param target_uuid: the uuid of the location (field Entity.uuid)
        @type target_uuid: str

        @param mi_uuid: the menu item to move UUID
        @type mi_uuid: str

        @returns: True if succeed to move the menu item, else return False
        @rtype: boolean
        """
        db = ImagingDatabase()
        db.setLocationSynchroState(loc_id, P2ISS.TODO)
        return db.moveItemDownInMenu4Location(loc_id, mi_uuid)

    def imagingServermenuMulticast(self, objmenu):
        try:
            if ImagingRpcProxy.checkThread[objmenu['location']]==False:
                ImagingRpcProxy.checkThread[objmenu['location']] = True
        except KeyError:
            ImagingRpcProxy.checkThread[objmenu['location']] = True
        finally:
            self.ClearMulticastMultiSessionParameters(objmenu['location'])
            time.sleep(2)
            a = threading.Thread(None, self.monitorsUDPSender, None, (objmenu,))
            a.start()
        location=objmenu['location']
        imaging_server = ImagingDatabase().getEntityUrl(location)
        i = ImagingApi(imaging_server.encode('utf8'))
        if i != None:
            deferred = i.imagingServermenuMulticast(objmenu)
            deferred.addCallback(lambda x: x)
        else:
            deferred = []
        return deferred

    def imagingClearMenuFromUuidAllLocation(self, uuid):
        obj={}
        ctx = self.currentContext
        obj['mac'] = ComputerManager().getMachineMac(ctx, {'uuid': uuid})
        obj['uuid']=uuid
        db = ImagingDatabase()
        locationName=[]
        location = db.getAllLocation()
        for t in location:
            self.imagingClearMenuforLocation( obj, t.url)
            locationName.append(t.name)
        return locationName

    def imagingClearMenuforLocation(self, obj, location):
        try:
            i = ImagingApi(location.encode('utf8'))
            if i != None:
                deferred = i.imagingClearMenu(obj)
                deferred.addCallback(lambda x: x)
            else:
                deferred = []
        except :
            deferred = []
        return deferred

    def imagingClearMenuFromUuid(self, uuid):
        obj={}
        ctx = self.currentContext
        obj['mac'] = ComputerManager().getMachineMac(ctx, {'uuid': uuid})
        obj['uuid']=uuid
        db = ImagingDatabase()
        try:
            location = db.getTargetsEntity([uuid])[0]
            url = chooseImagingApiUrl(location[0].uuid)
            i = ImagingApi(url.encode('utf8'))
            if i != None:
                deferred = i.imagingClearMenu(obj)
                deferred.addCallback(lambda x: x)
            else:
                deferred = []
        except :
            deferred = []
        return deferred

    ## Imaging server configuration
    def check_process_multicast(self, process):
        # controle execution process multicast
        location=process['location']
        imaging_server = ImagingDatabase().getEntityUrl(location)
        i = ImagingApi(imaging_server.encode('utf8'))
        if i != None:
            deferred = i.check_process_multicast(process)
            deferred.addCallback(lambda x: x)
        else:
            deferred = []
        return deferred

    def check_process_multicast_finish(self, process):
        # controle execution process multicast finish
        location=process['location']
        imaging_server = ImagingDatabase().getEntityUrl(location)
        i = ImagingApi(imaging_server.encode('utf8'))
        if i != None:
            deferred = i.check_process_multicast_finish(process)
            deferred.addCallback(lambda x: x)
        else:
            deferred = []
        return deferred

    def muticast_script_exist(self,process):
        # controle existance multicast script
        location=process['location']
        imaging_server = ImagingDatabase().getEntityUrl(location)
        i = ImagingApi(imaging_server.encode('utf8'))
        if i != None:
            deferred = i.muticast_script_exist(process)
            deferred.addCallback(lambda x: x)
        else:
            deferred = []
        return deferred


    def SetMulticastMultiSessionParameters(self, parameters):
        imaging_server = ImagingDatabase().getEntityUrl(parameters['location'])
        i = ImagingApi(imaging_server.encode('utf8'))
        if i != None:
            deferred = i.SetMulticastMultiSessionParameters(parameters)
            deferred.addCallback(lambda x: x)
        else:
            deferred = []
        return deferred

    def GetMulticastMultiSessionParameters(self, location):
        imaging_server = ImagingDatabase().getEntityUrl(location)
        i = ImagingApi(imaging_server.encode('utf8'))
        if i != None:
            deferred = i.GetMulticastMultiSessionParameters(location)
            deferred.addCallback(lambda x: x)
        else:
            deferred = []
        return deferred

    def ClearMulticastMultiSessionParameters(self, location):
        imaging_server = ImagingDatabase().getEntityUrl(location)
        i = ImagingApi(imaging_server.encode('utf8'))
        if i != None:
            deferred = i.ClearMulticastMultiSessionParameters(location)
            deferred.addCallback(lambda x: x)
        else:
            deferred = []
        return deferred

    def clear_script_multicast(self, process):
        #check if the script is installed multicast.sh
        try:
            if ImagingRpcProxy.checkThread[process['location']]==True:
                ImagingRpcProxy.checkThread[process['location']] = False
        except KeyError:
            ImagingRpcProxy.checkThread[process['location']] = False
        location=process['location']
        imaging_server = ImagingDatabase().getEntityUrl(location)
        i = ImagingApi(imaging_server.encode('utf8'))
        if i != None:
            deferred = i.clear_script_multicast(process)
            deferred.addCallback(lambda x: x)
        else:
            deferred = []
        return deferred

    def start_process_multicast(self,process):
        # Multicast start
        location=process['location']
        imaging_server = ImagingDatabase().getEntityUrl(location)
        i = ImagingApi(imaging_server.encode('utf8'))
        if i != None:
            deferred = i.start_process_multicast(process)
            deferred.addCallback(lambda x: x)
        else:
            deferred = []
        return deferred

    def statusReadFile (self, file):
        logger = logging.getLogger()
        logger.debug("statusReadFile %s"%file)
        if not path.isfile(file):
            return []
        fichier = open(file)
        lignes = fichier.readlines()
        fichier.close()
        return lignes

    def ClearFileStatusProcess(self):
        logger = logging.getLogger()
        logger.debug("ClearFileStatusProcess")
        fichier = open("/tmp/pulse2-synch-masters.out", "w")
        fichier.close()
        return True

    def statusProcessBarClone(self, listfilelog):
        logger = logging.getLogger()
        logger.debug("statusProcessBarClone %s"%listfilelog)
        data={}
        for f in listfilelog:
            data[f]="0 0% 0MB/s xx:xx:xx wait"
            if path.isfile("/tmp/%s"%f):
                if path.getsize("/tmp/%s"%f) > 0:
                    fichier = open("/tmp/%s"%f, "r")
                    lignes = fichier.readlines()
                    fichier.close()
                    #data[f]=str(lignes).split("\r")[-1]
                    kk=str(lignes[-1]).split("\r")[-1]
                    kk = kk.strip()
                    kkl=kk.split(" ")
                    kk = [x for x in kkl if x !=""]
                    if kk[1] == "0%" and len(kk) > 4 :
                        logger.debug("transfer terminer pour %s"%f)
                        data[f]="0 100% 0MB/s xx:xx:xx"
                    else :
                        data[f]=' '.join(kk)
                else:
                    logger.debug("file empty /tmp/%s"%f)
            else:
                logger.debug("file missing /tmp/%s"%f)
        return json.dumps(data)

    def startProcessClone(self, objetclone):
        test = self.checkProcessCloneMasterToLocation('/bin/bash /usr/bin/pulse2-synch-masters');
        #if test: return
        if len(test) > 0 : return
        self.ClearFileStatusProcess()
        logger = logging.getLogger()
        logger.debug("startProcessClone %s"%objetclone)
        if not path.isfile("/usr/bin/pulse2-synch-masters"):
            logger.debug("script /usr/bin/pulse2-synch-masters missing")
            return
        if len(objetclone['server_imaging']) == 0:
            #if objetclone['server_imaging'] == False:
            return
        for k,v in objetclone['server_imaging'].iteritems():
            logger.debug("/usr/bin/pulse2-synch-masters %s %s %s\n"%(fromUUID(objetclone['location']),fromUUID(k),objetclone['masteruuid']))
            args = ["nohup", "/bin/bash", "/usr/bin/pulse2-synch-masters", str(fromUUID(objetclone['location'])),str(fromUUID(k)),str(objetclone['masteruuid'])]
            logger.debug("objname == %s "%(args))
            subprocess.Popen(args)
        return

    def checkProcessCloneMasterToLocation(self, name):
        """
            check script
        """
        returnprocesspid=[]
        s = subprocess.Popen(   "ps aux | grep '%s' |grep -v grep | awk -F \" \" '{  print $2 }' "%name,
                                shell = True,
                                stdout = subprocess.PIPE
                           )
        for x in s.stdout:
            returnprocesspid.append(x.strip(' \t\n\r'))
        s.stdout.close()
        return returnprocesspid

    def monitorsUDPSender(self, objmenu):
        """
            Menu group regenerated immediately started transferring multicast udp
        """
        ImagingRpcProxy.checkThread={}
        ImagingRpcProxy.checkThreadData={}
        ImagingRpcProxy.checkThread[objmenu['location']] = True
        ImagingRpcProxy.checkThreadData[objmenu['location']]={'data': '', 'tranfert' : False}
        temp=10;
        while(ImagingRpcProxy.checkThread[objmenu['location']] == True):
            logging.getLogger().info("Multicast while object checkThread is %s"%ImagingRpcProxy.checkThread)
            for i in threading.enumerate():
                if i.getName() == "MainThread" and not i.isAlive():
                    logging.getLogger().debug("[Multicast TERMINATE  monitorsUDPSender]")
                    ImagingRpcProxy.checkThread[objmenu['location']] = False
                    return
            time.sleep(temp)
            logging.getLogger().debug("Multicast monitorsUDPSender")
            result=self.checkDeploymentUDPSender(objmenu)
            logging.getLogger().info("check whether Multicast transfer is in progress %s"%result)
            try:
                if ImagingRpcProxy.checkThreadData[objmenu['location']]['tranfert'] == True:
                    ImagingRpcProxy.checkThreadData[objmenu['location']]['tranfert'] = False
                    ImagingRpcProxy.checkThread[objmenu['location']] = False
                    logging.getLogger().debug("Multicast REGENERATE menu group %s [%s]"%(objmenu['description'],objmenu['group']))
                    self.synchroProfile(objmenu['group'])
                    return
            except KeyError:
                logging.getLogger().error("Multicast error monitorsUDPSender\n%s"%(traceback.format_exc()))
                ImagingRpcProxy.checkThreadData[objmenu['location']]={}
                ImagingRpcProxy.checkThreadData[objmenu['location']]['tranfert'] = False
        else:
            logging.getLogger().debug("Multicast REGENERATE menu group %s [%s]"%(objmenu['description'],objmenu['group']))
            self.synchroProfile(objmenu['group'])


    def checkDeploymentUDPSender(self, process):
        """
        check whether multicast transfer is in progress
        """
        resultat = False
        logger = logging.getLogger()
        logging.getLogger().debug("checkDeploymentUDPSender %s"%process)
        location=process['location']
        imaging_server = ImagingDatabase().getEntityUrl(location)
        i = ImagingApi(imaging_server.encode('utf8'))
        if i == None:
            logger.error("couldn't initialize the ImagingApi to %s"%(location))
            return [False, "couldn't initialize the ImagingApi to %s"%( location)]

        def treatResult(results):
            if results:
                ImagingRpcProxy.checkThreadData[process['location']]=results
                resultat=results
                return [resultat]
            else:
                ImagingRpcProxy.checkThreadData={}
                return []

        d = i.checkDeploymentUDPSender(process)
        d.addCallback(treatResult)
        return d

    def stop_process_multicast(self,process):
        # Multicast stop
        try:
            if ImagingRpcProxy.checkThread[process['location']]==True:
                ImagingRpcProxy.checkThread[process['location']] = False
        except KeyError:
            ImagingRpcProxy.checkThread[process['location']] = False
        location=process['location']
        imaging_server = ImagingDatabase().getEntityUrl(location)
        i = ImagingApi(imaging_server.encode('utf8'))
        if i != None:
            deferred = i.stop_process_multicast(process)
            deferred.addCallback(lambda x: x)
        else:
            deferred = []
        return deferred

    ###### IMAGES
    def imagingServerISOCreate(self, image_uuid, size, title):
        """
        Call the pserver to create an ISO image corresponding to a Pulse 2 image.
        The ISO image is bootable and allows to auto-restore the Pulse 2 image
        to a computer hard disk.
        For now, the creation process is started as a background process.

        @param image_uuid: UUID of the Pulse 2 image to convert to an ISO
        @type image_uuid: str
        @param size: media size, in bytes
        @type size: int
        @param title: title of the image, in UTF-8
        @type title: str
        @return: True if the creation process started
        @rtype: boolean
        """
        db = ImagingDatabase()
        logger = logging.getLogger()
        image, imaging_server = db.getImageAndImagingServer(image_uuid)

        i = ImagingApi(imaging_server.url.encode('utf8'))
        if i == None:
            logger.error("couldn't initialize the ImagingApi to %s"%(imaging_server.url))
            return [False, "couldn't initialize the ImagingApi to %s"%(imaging_server.url)]

        def treatResult(results, image = image, logger = logger):
            if results:
                logger.debug("ISO was created for image %s"%(image.uuid))
                return [results, "ISO was created for image %s"%(image.uuid)]
            else:
                logger.info("ISO wasn't created for image %s, look in the package server logs for more informations."%(image.uuid))
                return [results, "ISO wasn't created for image %s, look in the package server logs for more informations."%(image.uuid)]
        d = i.imagingServerISOCreate(image.uuid, size, title)
        d.addCallback(treatResult)
        return d

    def getTargetImage(self, uuid, target_type, image_uuid):
        """
        get one image from the database

        @param uuid: the target uuid
        @type uuid: str

        @param target_type: 'group' if it's a group, '' if it's a computer
        @type target_type: str

        @param image_uuid: the image uuid
        @type image_uuid: str

        @returns: a dict containing all the image information
        @rtype: dict
        """
        try:
            db = ImagingDatabase()
            target_type = self.__convertType(target_type, uuid)
            image = db.getTargetImage(uuid, target_type, image_uuid)
            return [True, xmlrpcCleanup(image.toH())]
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def __getTargetImages(self, id, target_type, start = 0, end = -1, filter = ''):
        # be careful the end is used for each list (image and master)
        db = ImagingDatabase()
        reti = map(lambda l: l.toH(), db.getPossibleImages(id, target_type, start, end, filter))
        counti = db.countPossibleImages(id, filter)

        retm = map(lambda l: l.toH(), db.getPossibleMasters(id, target_type, start, end, filter))
        countm = db.countPossibleMasters(id, filter)

        return {
            'images': [counti, xmlrpcCleanup(reti)],
            'masters': [countm, xmlrpcCleanup(retm)]
        }

    def getComputerImages(self, id, start = 0, end = -1, filter = ''):
        """
        get the list of all images and masters defined for a computer
        the list is divided into two parts : images and masters
        WARNING : the start and end element are applied to each list

        @param id: the uuid of the computer (field Target.uuid)
        @type id: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a dict of two elements : the images and the masters
        to content of each value is a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        return self.__getTargetImages(id, P2IT.COMPUTER, start, end, filter)

    def getProfileImages(self, id, start = 0, end = -1, filter = ''):
        """
        get the list of all masters defined for a profile
        the list is divided into two parts : images and masters
        but the image part is always empty
        WARNING : the start and end element are applied to each list

        @param id: the uuid of the profile (field Target.uuid)
        @type id: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a dict of two elements : the images and the masters
        to content of each value is a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        return self.__getTargetImages(id, P2IT.PROFILE, start, end, filter)

    def getLocationImages(self, loc_id, start = 0, end = -1, filter = ''):
        """
        get the list of all masters defined for a location

        @param loc_id: the uuid of the location (field Entity.uuid)
        @type loc_id: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        # Entities are names Location in the php part, here we convert them from Location to Entity
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getEntityMasters(loc_id, start, end, filter))
        count = db.countEntityMasters(loc_id, filter)
        return [count, xmlrpcCleanup(ret)]

    def getLocationMastersByUUID(self, loc_id, uuids):
        """
        get the masters defined by their uuids for that location)

        @param loc_id: the uuid of the location (field Entity.uuid)
        @type loc_id: str

        @param uuids: the masters uuids
        @type uuids: list

        @returns: the masters as a dict master_uuid: master
        @rtype: dict
        """
        db = ImagingDatabase()
        ret = db.getEntityMastersByUUID(loc_id, uuids)
        return xmlrpcCleanup(ret)

    def getComputersWithImageInEntity(self, uuidimagingServer):
        db = ImagingDatabase()
        ret = db.getComputerWithImageInEntity(uuidimagingServer)
        return xmlrpcCleanup(ret)


    # EDITION
    def addImageToTarget(self, item_uuid, target_uuid, params, target_type):
        """
        add an image to the target boot menu

        @param item_uuid: the image UUID
        @type: str

        @param target_uuid: the target UUID
        @type target_uuid: str

        @param params: the parameters of the association with the menu :
            * hidden : boolean, is the image shown in the menu
            * hidden_WOL : boolean, is the image shown in the WOL menu
            * default : boolean, is the image the default
            * default_WOL : boolean, is the image the default when booting after a WOL
            * name : the name
        @type params: dict

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: a pair :
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        db = ImagingDatabase()
        target_type = self.__convertType(target_type, target_uuid)
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = db.addImageToTarget(item_uuid, target_uuid, params)
            # Set custom menu flag to 1
            if target_type == P2IT.COMPUTER:
                self.setComputerCustomMenuFlag(target_uuid,1)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editImageToTarget(self, item_uuid, target_uuid, params, target_type):
        """
        edit the image to boot menu link parameters

        @param item_uuid: the image UUID
        @type: str

        @param target_uuid: the target UUID
        @type target_uuid: str

        @param params: the parameters of the association with the menu :
            * hidden : boolean, is the image shown in the menu
            * hidden_WOL : boolean, is the image shown in the WOL menu
            * default : boolean, is the image the default
            * default_WOL : boolean, is the image the default when booting after a WOL
            * name : the name
        @type params: dict

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: a pair :
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        db = ImagingDatabase()
        target_type = self.__convertType(target_type, target_uuid)
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = db.editImageToTarget(item_uuid, target_uuid, target_type, params)
            # Set custom menu flag to 1
            if target_type == P2IT.COMPUTER:
                self.setComputerCustomMenuFlag(target_uuid,1)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editImage(self, item_uuid, target_uuid, params, target_type):
        """
        edit an image

        @param item_uuid: the image UUID
        @type: str

        @param target_uuid: the target UUID
        @type target_uuid: str

        @param params: the parameters of the association with the menu :
            * hidden : boolean, is the image shown in the menu
            * hidden_WOL : boolean, is the image shown in the WOL menu
            * default : boolean, is the image the default
            * default_WOL : boolean, is the image the default when booting after a WOL
            * name : the name
        @type params: dict

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: a pair :
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        db = ImagingDatabase()
        target_type = self.__convertType(target_type, target_uuid)
        try:
            if db.isImageInMenu(item_uuid, target_uuid, target_type):
                db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = db.editImage(item_uuid, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editImageLocation(self, item_uuid, loc_id, params):
        """ same as editImage but for a location """
        db = ImagingDatabase()
        try:
            is_used = db.areImagesUsed([[item_uuid, loc_id, -1]])
            if is_used[item_uuid]:
                return [False, "cant modify a master if it's used by other targets"]
            ret = db.editImage(item_uuid, params)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def delImageToTarget(self, item_uuid, target_uuid, target_type):
        """
        remove an image from a boot menu

        @param item_uuid: the image UUID
        @type: str

        @param target_uuid: the target UUID
        @type target_uuid: str

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: a pair :
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        db = ImagingDatabase()
        target_type = self.__convertType(target_type, target_uuid)
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = db.delImageToTarget(item_uuid, target_uuid)
            # Set custom menu flag to 1
            if target_type == P2IT.COMPUTER:
                self.setComputerCustomMenuFlag(target_uuid,1)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def imageGetLogs(self, itemUUID):
        """
        @return: a deferred resulting to image logs as a list of string
        @rtype: Deferred
        """
        db = ImagingDatabase()
        image, ims = db.getImageAndImagingServer(itemUUID)
        api = ImagingApi(ims.url.encode('utf8'))
        if api != None:
            deferred = api.imageGetLogs(image.uuid)
            deferred.addCallback(lambda x: x)
        else:
            deferred = []
        return deferred

    def areImagesUsed(self, images): #image_uuid, target_uuid = None, target_type = None):
        """
        tell if the images are used by someone else than the target

        @param images: a list of triple (image_uuid, target_uuid, target_type)
        @type images: list

        @returns: a list of list. the second level is a pair :
        (target_uuid, target_type) of the targets that use that image in their boot menu
        @rtype: list
        """
        db = ImagingDatabase()
        ims = []
        if type(images[0]) == list:
            for im in images:
                i = [im[0], im[1], self.__convertType(im[2], im[1])]
                ims.append(i)
        else:
            i = [images[0], images[1], self.__convertType(images[2], images[1])]
            ims.append(i)

        return db.areImagesUsed(ims)

    def isServiceUsed(self, bs_uuid):
        """
        Return a list of computers or imaging server who use a BootService

        @param bs_uuid: a Boot Service UUID
        @type bs_uuid: str

        @return: list of computers and/or imaging server who use a BootService
        @rtype: list
        """
        db = ImagingDatabase()

        return db.isServiceUsed(bs_uuid)

    def imagingServerImageDelete(self, image_uuid):
        """
        delete an image from the database AND from the imaging server

        @param image_uuid: the image uuid (WARN : it's the uuid in the mmc, not in the package server)
        @type image_uuid: str

        @returns: a pair :
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        db = ImagingDatabase()
        logger = logging.getLogger()
        # try:
        if True:
            # check we are going to be able to remove from the menu
            is_used = self.areImagesUsed([[image_uuid, None, None]])
            is_used = is_used[image_uuid]
            #if is_used:
            if len(is_used) != 0:
                # some target have that image in their menu
                if not db.canRemoveFromMenu(image_uuid):
                    return [False, "Can't remove %s from some boot menus" % (image_uuid)]

            # remove from the imaging server
            im, ims = db.getImageAndImagingServer(image_uuid)
            i = ImagingApi(ims.url.encode('utf8'))
            if i == None:
                logger.error("couldn't initialize the ImagingApi to %s" % (ims.url))
                return [False, "couldn't initialize the ImagingApi to %s" % (ims.url)]

            def treatDel(results, image_uuid, db, logger):
                if not results:
                    logger.error("The package server failed to delete the image")
                    return [False, "The package server failed to delete the image"]

                try:
                    # remove all the remaining from the database
                    ret = db.imagingServerImageDelete(image_uuid)
                    return xmlrpcCleanup([True, ret])
                except Exception, e:
                    return xmlrpcCleanup([False, e])

            d = i.imagingServerImageDelete(im.uuid)
            d.addCallback(treatDel, image_uuid, db, logger)
            return d
        #except Exception, e:
        #    return xmlrpcCleanup([False, e])

    def addImageToLocation(self, item_uuid, loc_id, params):
        """ same as addImageToTarget but for a location """
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(loc_id, P2ISS.TODO)
            ret = db.addImageToEntity(item_uuid, loc_id, params)
            return xmlrpcCleanup([True, ret])
            # Applying this menu on all machines that have no custom_menu
            self.applyLocationDefaultBootMenu(loc_id)
        except Exception, e:
            raise e
            return xmlrpcCleanup([False, e])

    def editImageToLocation(self, item_uuid, loc_id, params):
        """ same as editImageToTarget but for a location """
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(loc_id, P2ISS.TODO)
            ret = db.editImageToEntity(item_uuid, loc_id, params)
            # Applying this menu on all machines that have no custom_menu
            self.applyLocationDefaultBootMenu(loc_id)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def delImageToLocation(self, menu_item_id, loc_id):
        """ same as delImageToTarget but for a location """
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(loc_id, P2ISS.TODO)
            ret = db.delImageToEntity(menu_item_id)
            # Applying this menu on all machines that have no custom_menu
            self.applyLocationDefaultBootMenu(loc_id)
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
        """
        get the boot services that are in a computer's boot menu

        @param id: the computer's UUID (Target.uuid)
        @type id: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        return self.__getTargetBootServices(id, P2IT.COMPUTER, start, end, filter)

    def getProfileBootServices(self, id, start = 0, end = -1, filter = ''):
        """
        get the boot services that are in a profile's boot menu

        @param id: the profile's UUID (Target.uuid)
        @type id: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        return self.__getTargetBootServices(id, P2IT.PROFILE, start, end, filter)

    def getPossibleBootServices(self, target_uuid, start = 0, end = -1, filter = ''):
        """
        get all the boot services that a target can use

        @param target_uuid: the target's UUID (Target.uuid)
        @type target_uuid: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getPossibleBootServices(target_uuid, start, end, filter))
        count = db.countPossibleBootServices(target_uuid, filter)
        return [count, xmlrpcCleanup(ret)]

    def getLocationBootServices(self, loc_id, start = 0, end = -1, filter = ''):
        """
        get all the boot services that a location can use

        @param loc_id: the location's UUID (Entity.uuid)
        @type loc_id: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        # Entities are names Location in the php part, here we convert them from Location to Entity
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getEntityBootServices(loc_id, start, end, filter))
        count = db.countEntityBootServices(loc_id, filter)
        return [count, xmlrpcCleanup(ret)]

    # EDITION
    def addServiceToTarget(self, bs_uuid, target_uuid, params, target_type):
        """
        add a boot service to a target boot menu

        @param bs_uuid: boot service uuid
        @type bs_uuid: str

        @param target_uuid: target's UUID (Target.uuid)
        @type target_uuid: str

        @param params: the parameters of the association with the menu :
            * hidden : boolean, is the image shown in the menu
            * hidden_WOL : boolean, is the image shown in the WOL menu
            * default : boolean, is the image the default
            * default_WOL : boolean, is the image the default when booting after a WOL
            * name : the name
        @type params: dict

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        db = ImagingDatabase()
        target_type = self.__convertType(target_type, target_uuid)
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = ImagingDatabase().addServiceToTarget(bs_uuid, target_uuid, params)
            # Set custom menu flag to 1
            if target_type == P2IT.COMPUTER:
                self.setComputerCustomMenuFlag(target_uuid,1)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def delServiceToTarget(self, bs_uuid, target_uuid, target_type):
        """
        remove a boot service from a target boot menu

        @param bs_uuid: boot service uuid
        @type bs_uuid: str

        @param target_uuid: target's UUID (Target.uuid)
        @type target_uuid: str

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        db = ImagingDatabase()
        target_type = self.__convertType(target_type, target_uuid)
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = ImagingDatabase().delServiceToTarget(bs_uuid, target_uuid)
            # Set custom menu flag to 1
            if target_type == P2IT.COMPUTER:
                self.setComputerCustomMenuFlag(target_uuid,1)
            return xmlrpcCleanup(ret)
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editServiceToTarget(self, bs_uuid, target_uuid, params, target_type):
        """
        edit a boot service already associated to a target boot menu

        @param bs_uuid: boot service uuid
        @type bs_uuid: str

        @param target_uuid: target's UUID (Target.uuid)
        @type target_uuid: str

        @param params: the parameters of the association with the menu :
            * hidden : boolean, is the image shown in the menu
            * hidden_WOL : boolean, is the image shown in the WOL menu
            * default : boolean, is the image the default
            * default_WOL : boolean, is the image the default when booting after a WOL
            * name : the name
        @type params: dict

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        db = ImagingDatabase()
        target_type = self.__convertType(target_type, target_uuid)
        if bs_uuid == '':
            return [False, "You are trying to access to editServiceToTarget without any Service ID."]
        if target_uuid == '':
            return [False, "You are trying to access to editServiceToTarget without any Target ID."]
        try:
            db.changeTargetsSynchroState([target_uuid], target_type, P2ISS.TODO)
            ret = ImagingDatabase().editServiceToTarget(bs_uuid, target_uuid, target_type, params)
            # Set custom menu flag to 1
            if target_type == P2IT.COMPUTER:
                self.setComputerCustomMenuFlag(target_uuid,1)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            raise e
            return xmlrpcCleanup([False, e])

    def addServiceToLocation(self, bs_uuid, location_id, params):
        """ same as addServiceToTarget for a location """
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(location_id, P2ISS.TODO)
            ret = ImagingDatabase().addServiceToEntity(bs_uuid, location_id, params)
            # Applying this menu on all machines that have no custom_menu
            self.applyLocationDefaultBootMenu(location_id)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def delServiceToLocation(self, bs_uuid, location_id):
        """ same as delServiceToTarget for a location """
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(location_id, P2ISS.TODO)
            ret = ImagingDatabase().delServiceToEntity(bs_uuid, location_id)
            # Applying this menu on all machines that have no custom_menu
            self.applyLocationDefaultBootMenu(location_id)
            return xmlrpcCleanup(ret)
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def editServiceToLocation(self, mi_uuid, location_id, params):
        """ same as editServiceToTarget for a location """
        db = ImagingDatabase()
        try:
            db.setLocationSynchroState(location_id, P2ISS.TODO)
            ret = ImagingDatabase().editServiceToEntity(mi_uuid, location_id, params)
            # Applying this menu on all machines that have no custom_menu
            self.applyLocationDefaultBootMenu(location_id)
            return xmlrpcCleanup([True, ret])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def removeService(self, bs_uuid, location_id, params):
        """ Remove / Delete a service (generally created by a post-imaging script) """
        db = ImagingDatabase()
        try:
            # Remove BootService in DB
            db.setLocationSynchroState(location_id, P2ISS.TODO)
            ret = ImagingDatabase().removeService(bs_uuid, location_id, params)
            if ret:
                # Delete .sh file
                url = chooseImagingApiUrl(location_id)
                i = ImagingApi(url.encode('utf8')) # TODO why do we need to encode....
                i.bsUnlinkShFile(ret)
            else:
                raise Exception("Error while removing boot service")
            return xmlrpcCleanup([True, None])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    ###### MENU ITEMS
    def getMenuItemByUUID(self, bs_uuid):
        """
        get the detail of a menu item for an uuid

        @param bs_uuid: the menu item UUID
        @type bs_uuid: str

        @returns: a dictionary containing the menu item details
        @rtype: dict
        """
        mi = ImagingDatabase().getMenuItemByUUID(bs_uuid)
        if mi != None:
            return xmlrpcCleanup(mi.toH())
        return False

    ###### LOGS
    def __getTargetImagingLogs(self, id, target_types, start = 0, end = -1, filter = ''):
        db = ImagingDatabase()
        ret = []
        count = 0
        for tt in target_types:
            ret += map(lambda l: l.toH(), db.getImagingLogsOnTargetByIdAndType(id, tt, start, end, filter))
            count += db.countImagingLogsOnTargetByIdAndType(id, tt, filter)
        return [count, xmlrpcCleanup(ret)]

    def getComputerLogs(self, id, start = 0, end = -1, filter = ''):
        """
        get all the imaging logs of a computer

        @param id: the computer UUID (Target.uuid)
        @type id: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        return self.__getTargetImagingLogs(id, [P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE], start, end, filter)

    def getProfileLogs(self, id, start = 0, end = -1, filter = ''):
        """
        get all the imaging logs of a profile

        @param id: the profile UUID (Target.uuid)
        @type id: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        return self.__getTargetImagingLogs(id, [P2IT.PROFILE], start, end, filter)

    def getLogs4Location(self, location_uuid, start = 0, end = -1, filter = ''):
        """
        get all the imaging logs of all the elements of a location

        @param location_uuid: the entity UUID (Entity.uuid)
        @type location_uuid: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        if location_uuid == False:
            return [0, []]
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getImagingLogs4Location(location_uuid, start, end, filter))
        count = db.countImagingLogs4Location(location_uuid, filter)
        return [count, xmlrpcCleanup(ret)]

    ###### IMAGING API CALLS
    def getGlobalStatus(self, location):
        """
        get an imaging server status

        @param location: the location UUID (Entity.uuid)
        @type location: str

        @returns: a dict containing disk usage....
        @rtype: dict
        """
        def processResults(results):
            assert(type(results) == dict)
            if results:
                # add short_status from the database
                status = ImagingDatabase().getEntityStatus(location)
                results['short_status'] = status
            return xmlrpcCleanup(results)

        url = chooseImagingApiUrl(location)
        d = ImagingApi(url).imagingServerStatus()
        d.addCallback(processResults)
        return d

    ####### IMAGING SERVER
    def getAllNonLinkedImagingServer(self, start = 0, end = -1, filter = ''):
        """
        get all imaging servers that are not linked to any location

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: return a list of two elements :
            1) the size of the list
            2) the list delimited by start and end
        @rtype: list
        """
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getAllNonLinkedImagingServer(start, end, filter))
        count = db.countAllNonLinkedImagingServer(filter)
        return [count, xmlrpcCleanup(ret)]

    def linkImagingServerToLocation(self, is_uuid, loc_id, loc_name):
        """
        link an imaging server to a location

        @param is_uuid: the imaging server UUID
        @type is_uuid: str

        @param loc_id: the location UUID (Entity.uuid)
        @type loc_id: str

        @param loc_name: the location name
        @type loc_name: str

        @returns: a pair :
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        logging.getLogger().debug("linkImagingServerToLocation : is_uuid %s loc_id %s loc_name%s" % (is_uuid,loc_id,loc_name))
        db = ImagingDatabase()
        try:
            ret = db.linkImagingServerToEntity(is_uuid, loc_id, loc_name)
            my_is = db.getImagingServerByUUID(is_uuid)
            logging.getLogger().debug("getImagingServerByUUID : is_uuid %s " % (is_uuid))
            Pulse2Manager().putPackageServerEntity(my_is.packageserver_uuid, loc_id)
            db.setLocationSynchroState(loc_id, P2ISS.TODO)
        except Exception, e:
            logging.getLogger().warn("Imaging.linkImagingServerToEntity : %s" % e)
            return [False, "Failed to link Imaging Server to Entity : %s" % e]

        return [True, ret]

    def unlinkImagingServerToLocation(self, is_uuid, loc_id):
        """
        Inverse method to linkImagingServerToLocation: unlink an imaging server

        @param is_uuid: the imaging server UUID
        @type is_uuid: str

        @param loc_id: the location UUID (Entity.uuid)
        @type loc_id: str

        @returns: a pair :
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        logging.getLogger().debug("unlinkImagingServerToLocation : is_uuid %s loc_id %s " % (is_uuid,loc_id))
        db = ImagingDatabase()
        success1 = success2 = False
        try:
            success1 = db.unlinkImagingServerToEntity(is_uuid)
            success2 = Pulse2Manager().delPackageServerEntity(loc_id)
        except Exception, e:
            logging.getLogger().warn("Imaging.unlinkImagingServerToEntity : %s" % e)

        if not success1 :
            logging.getLogger().warn("Failed to unassociate the imaging server to entity:")
        if not success2 :
            logging.getLogger().warn("Failed to unassociate the package server to entity:")

        return [success1, success2]


    def getImagingServerConfig(self, location):
        """
        get an imaging server configuration

        @param location: the location UUID (Entity.uuid)
        @type location: str

        @returns: a pair:
            * the imaging server configuration as a dict
            * the imaging server default menu as a dict
        @rtype: list
        """
        imaging_server = ImagingDatabase().getImagingServerByEntityUUID(location)
        default_menu = ImagingDatabase().getEntityDefaultMenu(location)
        if imaging_server and default_menu:
            return xmlrpcCleanup((imaging_server.toH(), default_menu.toH()))
        elif default_menu:
            return [False, ":cant find imaging server linked to location %s" % (location)]
        elif imaging_server:
            return [False, ":cant find the default menu for location %s" % (location), xmlrpcCleanup(imaging_server.toH())]

    def getClonezillaSaverParams(self, location_uuid):
        return ImagingDatabase().getClonezillaSaverParams(location_uuid)

    def getClonezillaRestorerParams(self, location_uuid):
        return ImagingDatabase().getClonezillaRestorerParams(location_uuid)

    def getPXEPasswordHash(self, location_uuid):
        return ImagingDatabase().getPXEPasswordHash(location_uuid)

    def setImagingServerConfig(self, location, config):
        """
        set an imaging server configuration

        @param location: the location UUID (Entity.uuid)
        @type location: str

        @param config:
        @type config: dict

        @returns: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        db = ImagingDatabase()
        # Set PXE params
        if 'pxe_password' in config or 'language' in config:
            db.setLocationPXEParams(location, config)
        # Set Clonezilla params
        if 'clonezilla_saver_params' in config or 'clonezilla_restorer_params' in config:
            db.setLocationClonezillaParams(location, config)
        #
        menu = db.getEntityDefaultMenu(location)
        menu = menu.toH()
        try:
            db.setLocationSynchroState(location, P2ISS.TODO)
            db.checkLanguage(location, config['language'])
            # Regenerate bootmenus
            self.SynchroAllLocationComputers(location)
            return xmlrpcCleanup([db.modifyMenu(menu['imaging_uuid'], config)])
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def doesLocationHasImagingServer(self, loc_id):
        """
        check if a location has an imaging server associated

        @param loc_id: the location UUID (Entity.uuid)
        @type loc_id: str

        @returns: true if the location has an imaging server
        @rtype: boolean
        """
        return ImagingDatabase().doesLocationHasImagingServer(loc_id)

    ###### REGISTRATION
    def isTargetRegister(self, uuid, target_type):
        """
        check if a target has already been registered or not

        @param uuid: the target's UUID (Target.uuid)
        @type uuid: str

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: true if the target has been registered
        @rtype: boolean
        """
        return ImagingDatabase().isTargetRegister(uuid, target_type)

    def isComputerRegistered(self, machine_uuid):
        """ see isTargetRegister """
        return self.isTargetRegister(machine_uuid, P2IT.COMPUTER)

    def isComputerInProfileRegistered(self, machine_uuid):
        """ see isTargetRegister """
        return self.isTargetRegister(machine_uuid, P2IT.COMPUTER_IN_PROFILE)

    def canIRegisterThisComputer(self, computerUUID):
        """
        look that computer's profile state :
            * if the computer is already declared => NOK
                (avoid some useless checks, and don't declare an already registered computer)
            * if the computer has no profile => OK
            * if the computer has a profile :
                * if the profile is registered => OK
                * if the profile is not registered => NOK

        @param computerUUID: the computer's UUID (Target.uuid)
        @type computerUUID:str

        @returns: true if the computer can be registered
        @rtype: boolean
        """
        logger = logging.getLogger()
        if self.isComputerRegistered(computerUUID):
            logger.debug("canIRegisterThisComputer %s : %s", computerUUID, "isComputerRegistered")
            return [False, False]

        profile = ComputerProfileManager().getComputersProfile(computerUUID)
        if profile == None:
            logger.debug("canIRegisterThisComputer %s : %s", computerUUID, "profile = None")
            return [True]

        profile = profile.toH()

        # ... here we take the id because it's what we always take... but it should be the uuid
        if self.isProfileRegistered(profile['id']):
            logger.debug("canIRegisterThisComputer %s : %s", computerUUID, "isProfileRegistered")
            return [True, profile['id']]

        logger.debug("canIRegisterThisComputer %s : %s", computerUUID, "final false")
        return [False, profile['id']]


    def delComputersImaging(self, computers_UUID, backup):
        """
        @param computers_UUID: list of computers uuids
        @type computers_UUID: list

        @param backup: do we do a backup or not
        @type backup: bool

        @returns: a couple of :
            0 : a boolean state
            1 : the list of uuids of the target that failed to unregister
        @rtype: list
        """
        if type(computers_UUID) != list:
            computers_UUID = [computers_UUID]
        ret = computersUnregister(computers_UUID, backup)
        return ret



    def checkComputerForImaging(self, computerUUID):
        """
        @return: 0 if the computer can be registered into the imaging module
        @rtype: int
        """
        ctx = self.currentContext
        query = getComputersNetwork_filtered(ctx, {'uuid':computerUUID})
        try:
            macaddress = query[0][1]['macAddress']
            macaddress = [x for x in macaddress if x]
        except KeyError:
            macaddress = []
        except IndexError:
            macaddress = []
        # if we have more than one mac address, we ask the user to chose which NIC he wants
        #if macaddress == False:
        if len(macaddress) < 1:
            # No MAC address
            ret = 1
        elif pulse2.utils.isLinuxMacAddress(macaddress[0]):
            # Valid MAC address
            ret = 0
        else:
            # Invalid MAC address
            ret = 3
        return ret

    def getProfileNetworks(self, profileUUID):
        uuids = [c.uuid for c in ComputerProfileManager().getProfileContent(profileUUID)]
        ctx = self.currentContext
        networks = getComputersNetwork_filtered(ctx, {'uuids': uuids})

        return xmlrpcCleanup(networks)


    def checkProfileForImaging(self, profileUUID):
        """
        @return: 0 if the profile can be registered into the imaging module
        @rtype: int
        """
        logger = logging.getLogger()
        ret = 0
        ctx = self.currentContext
        uuids = [c.uuid for c in ComputerProfileManager().getProfileContent(profileUUID)]
        #if uuids:
        if len(uuids):
            h_macaddresses = getJustOneMacPerComputer(ctx, ComputerManager().getMachineMac(ctx, {'uuids':uuids}))
            macaddresses = h_macaddresses.values()
            if '' in macaddresses:
                # Some computers don't have a MAC address
                logger.info("Some computers don't have any MAC address in the profile %s" % profileUUID)
                ret = 2
            elif len(uuids) < len(macaddresses):
                # Some computers have more than one MAC address
                logger.info("Some computers have more than one MAC address in the profile %s" % profileUUID)
                ret = 3
            elif len(uuids) > len(macaddresses):
                # Some computers don't have a MAC address
                list_of_fail = uuids
                for uuid in h_macaddresses.keys():
                    if uuid in list_of_fail:
                        list_of_fail.remove(uuid)
                logger.info("Some computers don't have any MAC address in the profile %s (%s)" % (profileUUID, str(list_of_fail)))
                ret = 2
            else:
                ret = 0
                # Check all MAC addresses
                i = 0
                for uuid, mac in h_macaddresses.iteritems():
                    if not pulse2.utils.isLinuxMacAddress(mac):
                        logger.info("The computer %s don't have a valid MAC address" % uuid)
                        ret = 4
                        break
                    i += 1
#            if not ret:
#                # Still no error ? Now checks that all the computers belong to the
#                # same entity
#                locations = ComputerLocationManager().getMachinesLocations(uuids)
#                locations_uuid = [l['uuid'] for l in locations.values() if 'uuid' in l]
#                if len(locations_uuid) != len(uuids):
#                    # some computers have no location ?
#                    logger.info("Some computers don't have location in the profile %s" % profileUUID)
#                    ret = 5
#                elif locations_uuid.count(locations_uuid[0]) != len(locations_uuid):
#                    # All the computers don't belong to the same location
#                    logger.info("All the computers don't belong to the same location (%s)" % profileUUID)
#                    ret = 6
        return ret

    def isProfileRegistered(self, profile_uuid):
        """ see isTargetRegister """
        return self.isTargetRegister(profile_uuid, P2IT.PROFILE)

    ###### Synchronisation
    def resetSynchroState(self, uuid, target_type):
        """
        reset the target synchronisation state (used in case the synchro failed to go
        back to a stable state (TODO or DONE)

        @param uuid: the target's UUID (Target.uuid)
        @type uuid: str
        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: the reset status (True if ok, False if not)
        @rtype: boolean
        """
        db = ImagingDatabase()
        target_type = self.__convertType(target_type, uuid)
        try:
            ret = db.changeTargetsSynchroState([uuid], target_type, P2ISS.TODO)
            return ret
        except Exception, e:
            self.logger.warn("Error while resetSynchroState %s"%(uuid))
            self.logger.warn(e)
        return False

    def getTargetSynchroState(self, uuid, target_type):
        """
        get the synchronization state of a target

        @param uuid: the target's UUID (Target.uuid)
        @type uuid: str

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: the synchronization state associated to that target's boot menu,
        it's a dict containing an id and a name
        @rtype: dict
        """
        ret = ImagingDatabase().getTargetsSynchroState([uuid], target_type)
        if ret:
            return ret[0]
        else:
            raise Exception("Can't get a synchro state for %s"%uuid)

    def getTargetsCustomMenuFlag(self, uuid, target_type):
        """
        get the custom menu flag of a target menu

        @param uuid: the target's UUID (Target.uuid)
        @type uuid: str

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: custom_menu flag (0 or 1)
        @rtype: int
        """
        ret = ImagingDatabase().getTargetsCustomMenuFlag([uuid], target_type)
        if ret != None:
            return ret
        else:
            raise Exception("Can't get a custom menu flag for %s"%uuid)

    def setComputerCustomMenuFlag(self, uuid, value):
        ret = ImagingDatabase().setComputerCustomMenuFlag([uuid], value)
        if ret:
            return True
        else:
            return False

    def getCustomMenuCount(self, location):
        return ImagingDatabase().getCustomMenuCount(location)

    def getCustomMenuCountdashboard(self, location):
        return ImagingDatabase().getCustomMenuCountdashboard(location)

    def getCustomMenubylocation(self, location):
        return ImagingDatabase().getCustomMenubylocation(location)

    def getComputerSynchroState(self, uuid):
        """ see getTargetSynchroState """
        if self.isTargetRegister(uuid, P2IT.COMPUTER):
            ret = self.getTargetSynchroState(uuid, P2IT.COMPUTER)
        elif self.isTargetRegister(uuid, P2IT.COMPUTER_IN_PROFILE):
            ret = self.getTargetSynchroState(uuid, P2IT.COMPUTER_IN_PROFILE)
        else:
            return {'id': 0}
        return xmlrpcCleanup(ret.toH())

    def getComputerCustomMenuFlag(self, uuid):
        """ see getTargetsCustomMenuFlag """
        if self.isTargetRegister(uuid, P2IT.COMPUTER):
            ret = self.getTargetsCustomMenuFlag(uuid, P2IT.COMPUTER)
        elif self.isTargetRegister(uuid, P2IT.COMPUTER_IN_PROFILE):
            ret = self.getTargetsCustomMenuFlag(uuid, P2IT.COMPUTER_IN_PROFILE)
        else:
            return None
        return ret


    def getProfileSynchroState(self, uuid):
        """ see getTargetSynchroState """
        if not self.isTargetRegister(uuid, P2IT.PROFILE):
            return {'id': 0}
        ret = self.getTargetSynchroState(uuid, P2IT.PROFILE)
        return xmlrpcCleanup(ret.toH())

    def getLocationSynchroState(self, uuid):
        """
        get the synchronization state of a location

        @param uuid: the location's UUID (Entity.uuid)
        @type uuid: str

        @returns: the synchronization state associated to that location's boot menu,
        it's a dict containing an id and a name
        @rtype: dict
        """
        if not self.doesLocationHasImagingServer(uuid):
            return {'id': 0}
        ret = ImagingDatabase().getLocationSynchroState(uuid)
        if type(ret) != list:
            ret = ret.toH()
        return xmlrpcCleanup(ret)

    def __generateDefaultSuscribeMenu(self, logger, db, imaging_server_uuid):
        location = db.getImagingServerEntity(imaging_server_uuid)
        if location == None:
            # Package server has not been registered, we return an empty menu
            return {}

        menu = db.getDefaultSuscribeMenu(location)
        menu_items = db.getMenuContent(menu.id, P2IM.ALL, 0, -1, '', None, location.uuid)
        menu = menu.toH()
        menu, menu_items, h_pis = generateMenusContent(menu, menu_items, None)
        ims = h_pis.keys()
        a_pis = db.getImagesPostInstallScript(ims, None, location.uuid)
        for pis, im, name_i18n, desc_i18n, pis_order in a_pis:
            name = pis.default_name
            desc = pis.default_desc
            if name_i18n != None:
                name = name_i18n.label
            if desc_i18n != None:
                desc = desc_i18n.label
            pis = {
                'id':pis.id,
                'name':name,
                'desc':desc,
                'value':pis.value,
                'order':pis_order
            }
            a_targets = h_pis[im.id]
            for loc_uuid, t_uuid, order in a_targets:
                # loc_uuid = None
                # t_uuid = None
                if not menu['images'][order].has_key('post_install_script'):
                #if not 'post_install_script' in menu['images'][order]:
                    menu['images'][order]['post_install_script'] = []
                menu['images'][order]['post_install_script'].append(pis)
        menu['language'] = db.getLocLanguage(location.uuid)
        return menu

    def __generateLocationMenu(self, logger, db, loc_uuid):
        location = db.getEntityByUUID(loc_uuid)
        menu = db.getDefaultSuscribeMenu(location)
        menu_items = db.getMenuContent(menu.id, P2IM.ALL, 0, -1, '', None, loc_uuid)
        menu = menu.toH()
        menu, menu_items, h_pis = generateMenusContent(menu, menu_items, loc_uuid)
        ims = h_pis.keys()
        a_pis = db.getImagesPostInstallScript(ims, None, loc_uuid)
        for pis, im, name_i18n, desc_i18n, pis_order in a_pis:
            pis = {
                'id':pis.id,
                'name':pis.default_name,
                'desc':pis.default_desc,
                'value':pis.value,
                'order':pis_order
            }
            a_targets = h_pis[im.id]
            for loc_uuid, t_uuid, order in a_targets:
                if not menu['images'][order].has_key('post_install_script'):
                #if not 'post_install_script' in menu['images'][order]:
                    menu['images'][order]['post_install_script'] = []
                menu['images'][order]['post_install_script'].append(pis)
        menu['language'] = db.getLocLanguage(location.uuid)
        return menu

    def __synchroLocation(self, loc_uuid):
        logger = logging.getLogger()
        db = ImagingDatabase()
        db.setLocationSynchroState(loc_uuid, P2ISS.RUNNING)

        try:
            menu = self.__generateLocationMenu(logger, db, loc_uuid)
            def cb_fail(error, location_uuid = loc_uuid, menu = menu, logger = logger):
                db.setLocationSynchroState(location_uuid, P2ISS.TODO)
                logger.error("couldn't run imagingServerDefaultMenuSet for location %s (in the errback)"%(location_uuid))
                return False

            def treatFailures(result, location_uuid = loc_uuid, menu = menu, logger = logger):
                if result:
                    db.setLocationSynchroState(location_uuid, P2ISS.DONE)
                else:
                    db.setLocationSynchroState(location_uuid, P2ISS.TODO)
                return result

            url = chooseImagingApiUrl(loc_uuid)
            i = ImagingApi(url.encode('utf8')) # TODO why do we need to encode....
            if i == None: # do fail
                db.setLocationSynchroState(loc_uuid, P2ISS.TODO)
                logger.error("couldn't initialize the ImagingApi to %s"%(url))
                return defer.fail()
            d = i.imagingServerDefaultMenuSet(menu)
            d.addCallback(treatFailures).addErrback(cb_fail)
            return d
        except Exception, e:
            logger.error("Error trying to set default menu (location: %s): %s" % \
                             (loc_uuid, e))
            db.setLocationSynchroState(loc_uuid, P2ISS.TODO)
        return defer.fail()

    def __synchroTargets(self, uuids, target_type, macs = {}, ctx = None, wol = False):
        """
        synchronize targets with their imaging servers

        @param uuids: the targets UUID (Target.uuid)
        @type uuids: list

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        but as to be the same for all the targets
        @type target_type: str or int

        @param wol: this parameter is used to update bootmenu for Wake-On-Lan
        If wol is true, generated bootmenu is the WOL one
        @type wol: bool

        @returns: the list of uuids of the target that failed to synchronize
        @rtype: list
        """
        if ctx == None:
            ctx = self.currentContext
        return synchroTargets(ctx, uuids, target_type, macs = macs, wol = wol)

    def synchroComputer(self, uuid, mac = False, wol = False):
        """ see __synchroTargets """
        logging.getLogger().debug("I'm going to synchronize computer %s bootmenu, Wake-on-lan is %s" % (uuid, wol and 'on' or 'off'))
        macs = mac and {uuid: mac} or {}
        if self.isTargetRegister(uuid, P2IT.COMPUTER):
            ret = self.__synchroTargets([uuid], P2IT.COMPUTER, macs = macs, wol = wol)
        elif self.isTargetRegister(uuid, P2IT.COMPUTER_IN_PROFILE):
            ret = self.__synchroTargets([uuid], P2IT.COMPUTER_IN_PROFILE, macs = macs, wol = wol)
        else:
            return False
        return xmlrpcCleanup(ret)

    def synchroProfile(self, uuid):
        """ see __synchroTargets """
        if not self.isTargetRegister(uuid, P2IT.PROFILE):
            return False
        ret = self.__synchroTargets([uuid], P2IT.PROFILE)
        return xmlrpcCleanup(ret)

    def synchroLocation(self, uuid):
        """
        synchronize all the configuration from the database to the imaging server
        also synchronize all the targets contained in this location

        @param uuid: the location's UUID (Entity.uuid)
        @type uuid: str

        @returns: the list of uuids of the target that failed to synchronize
        @rtype: list
        """
        logger = logging.getLogger()
        db = ImagingDatabase()
        dl = []
        def __getUUID(x):
            x = x[0].toH()
            return x['uuid']

        # get computers in location that need synchro
        uuids = db.getComputersThatNeedSynchroInEntity(uuid)
        uuids = map(__getUUID, uuids)

        def treatComputers(results):
            logger.debug("treatComputers>>>>>>")
            logger.debug(results)

        #if uuids :
        if len(uuids) != 0:
            d1 = self.__synchroTargets(uuids, P2IT.COMPUTER)
            d1.addCallback(treatComputers)
            dl.append(d1)

        # get profiles in location that need synchro
        pids = db.getProfilesThatNeedSynchroInEntity(uuid)
        pids = map(__getUUID, pids)

        def treatProfiles(results):
            logger.debug("treatProfiles>>>>>>")
            logger.debug(results)

        #if pids:
        if len(pids) != 0:
            d2 = self.__synchroTargets(pids, P2IT.PROFILE)
            if type(d2) == list and d2[0]:
                pass
            else:
                d2.addCallback(treatProfiles)
                dl.append(d2)

        # get computers in profiles in location that need synchro
        pids = db.getComputersInProfileThatNeedSynchroInEntity(uuid)
        pids = map(__getUUID, pids)

        def treatComputersInProfile(results):
            logger.debug("treatComputersInProfile>>>>>>")
            logger.debug(results)

        #if pids:
        if len(pids) != 0:
            d3 = self.__synchroTargets(pids, P2IT.COMPUTER_IN_PROFILE)
            if type(d3) == list and d3[0]:
                pass
            else:
                d3.addCallback(treatComputersInProfile)
                dl.append(d3)

        # synchro the location
        def treatLocation(results):
            logger.debug("treatLocation>>>>>>")
            if results:
                logger.debug(results)
            else:
                logger.error(results)
                db.setLocationSynchroState(uuid, P2ISS.TODO)
                raise Exception("Error while synchronizing location")

        d4 = self.__synchroLocation(uuid)
        d4.addCallback(treatLocation)
        dl.append(d4)

        def sendResult(results):
            return xmlrpcCleanup(results)

        dl = defer.DeferredList(dl)
        dl.addCallback(sendResult)
        return dl

    def getProfileLocation(self, uuid):
        """ get Location of given Profile """
        return ImagingDatabase().getProfileLocation(uuid)

    ###### Menus
    def getDefaultMenuItem(self, uuid):
        """
        Getting of default menu entry from the database.

        @param uuid: UUID of computer
        @type uuid: str

        @return: True and menu item order if success
        @rtype: tuple
        """
        menu = self.getMyMenuComputer(uuid)
        if menu :
            if "fk_default_item" in menu[1]:
                item_id = menu[1]["fk_default_item"]
                try:
                    order = ImagingDatabase().getDefaultMenuItemOrder(item_id)[0].order
                    return [True, order]
                except Exception:
                    logging.getLogger.warn("Get default menu item failed for UUID:%s" % uuid)
        return [False, 0]


    def getMyMenuTarget(self, uuid, target_type):
        """
        get a target's boot menu and configuration
        it can come from the target itself,
        or from it's profile if it's a computer,
        or from it's entity whatever it is.

        @param uuid: the target's UUID (Target.uuid)
        @type uuid: str

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: a couple:
            * from where the menu comes
            * the menu as a dict
        @rtype: list
        """
        try:
            ret = ImagingDatabase().getMyMenuTarget(uuid, target_type)
        except NoImagingServerError:
            return [False, 'ERROR', P2ERR.ERR_NEED_IMAGING_SERVER_REGISTRATION, "You first need to register your imaging server."]
        if ret[1]:
            ret[1] = ret[1].toH()
        return ret

    def setMyMenuTarget(self, uuid, params, target_type):
        """
        set a boot menu and configuration for a target

        @param uuid: the target's UUID (Target.uuid)
        @type uuid: str

        @param params: all the values to define that menu
        @type params: dict

        @param target_type: the target type can be one of those two :
            1) '' or P2IT.COMPUTER (1) for a computer
            2) 'group' or P2IT.PROFILE (2) for a profile
        @type target_type: str or int

        @returns: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        db = ImagingDatabase()
        isRegistered = db.isTargetRegister(uuid, target_type)

        if not isRegistered and target_type == P2IT.COMPUTER and db.isTargetRegister(uuid, P2IT.COMPUTER_IN_PROFILE):
            # if the computer change from a profile to it's own registering,
            # we remove the COMPUTER_IN_PROFILE target and register a COMPUTER one
            target_type = P2IT.COMPUTER_IN_PROFILE
            isRegistered = True

        try:
            ret, target = db.setMyMenuTarget(uuid, params, target_type)
            db.changeTargetsSynchroState([uuid], target_type, P2ISS.TODO)
        except Exception, e:
            return [False, "setMyMenuTarget : %s" % str(e)]

        if not isRegistered:
            # send the menu to the good imaging server to register the computer
            logger = logging.getLogger()
            db.changeTargetsSynchroState([uuid], target_type, P2ISS.RUNNING)

            if target_type == P2IT.PROFILE:
                pid = uuid
                uuids = map(lambda c: c.uuid, ComputerProfileManager().getProfileContent(pid))
            else:
                uuids = [uuid]

            #if uuids == False:
            if len(uuids) == 0:
                db.changeTargetsSynchroState([uuid], target_type, P2ISS.DONE)
                return [True]

            # Getting menus
            distinct_loc = generateMenus(logger, db, uuids)

            if target_type == P2IT.COMPUTER:
                # Getting current computer location
                location = db.getTargetsEntity([uuid])[0]

                url = chooseImagingApiUrl(location[0].uuid)
                i = ImagingApi(url.encode('utf8')) # TODO why do we need to encode....
                if i != None:
                    # Current computer's menu is in distinct_loc dictionnary
                    # We're treating a computer, so distinct_loc contains one loc_uuid
                    # we can make a for in:
                    for loc_uuid in distinct_loc:
                        menu = distinct_loc[loc_uuid][1]

                    imagingData = {'menu':menu, 'uuid':uuid}
                    ctx = self.currentContext
                    macs = ComputerManager().getMachineMac(ctx, {'uuid': uuid})
                    MACAddress = getJustOneMacPerComputer(ctx, macs)[uuid]

                    def treatRegister(result, location = location, uuid = uuid, db = db):
                        if result:
                            db.changeTargetsSynchroState([uuid], target_type, P2ISS.DONE)
                            return [True]
                        else:
                            # revert the target registering!
                            db.changeTargetsSynchroState([uuid], target_type, P2ISS.INIT_ERROR)
                            return [False, 'P2ISS.INIT_ERROR']

                    d = i.computerRegister(params['target_name'], MACAddress, imagingData)
                    d.addCallback(treatRegister)
                    return d
                else:
                    logger.error("couldn't initialize the ImagingApi to %s"%(url))
                    db.changeTargetsSynchroState([uuid], target_type, P2ISS.TODO)
                    return [False, ""]
            elif target_type == P2IT.PROFILE:
                pid = uuid
                defer_list = []
                uuids = []
                for loc_uuid in distinct_loc:
                    uuids.extend(distinct_loc[loc_uuid][1].keys())
                ctx = self.currentContext
                hostnames = ComputerManager().getMachineHostname(ctx, {'uuids':uuids})
                h_hostnames = {}
                if hostnames:
                    if type(hostnames) == list:
                        for computer in hostnames:
                            h_hostnames[computer['uuid']] = computer['hostname']
                    else:
                        h_hostnames[hostnames['uuid']] = hostnames['hostname']
                params['hostnames'] = h_hostnames

                # if 'choose_network_profile' in params, there is at least more than
                # one computer with more than one network card
                if 'choose_network_profile' in params:
                    h_macaddress = {}
                    networks = getComputersNetwork_filtered(ctx, {'uuids': uuids})[0][1]
                    keys = networks['networkUuids']
                    values = networks['macAddress']
                    # [Memo] uuidMacDict = {'NIC_UUID': 'Mac_adress', etc.}
                    uuidMacDict = dict(zip(keys, values))

                    for uuid in uuids:
                        if uuid in params['choose_network_profile']:
                            if params['choose_network_profile'][uuid] in uuidMacDict:
                                # if Target have more than one ethernet card
                                h_macaddress[uuid] = uuidMacDict[params['choose_network_profile'][uuid]]
                            else:
                                # else, get the good one
                                h_macaddress[uuid] = getJustOneMacPerComputer(ctx, ComputerManager().getMachineMac(ctx, {'uuids': uuids}))
                        else:
                            logger.warn('Imaging on group: %s doesn\'t exists in choose_network_profile key' % uuid)
                else:
                    h_macaddress = getJustOneMacPerComputer(ctx, ComputerManager().getMachineMac(ctx, {'uuids': uuids}))

                try:
                    params['target_name'] = '' # put the real name!
                    db.setProfileMenuTarget(uuids, pid, params)
                except Exception, e:
                    logger.error("failed to setProfileMenuTarget for computers in profile %s"%(pid))
                    db.changeTargetsSynchroState(uuids, P2IT.COMPUTER_IN_PROFILE, P2ISS.TODO)
                    return [False, "setProfileMenuTarget : %s" % (str(e))]

                for loc_uuid in distinct_loc:
                    url = distinct_loc[loc_uuid][0]
                    menus = distinct_loc[loc_uuid][1]
                    # to do again when computerRegister is plural
                    i = ImagingApi(url.encode('utf8')) # TODO why do we need to encode....
                    if i != None:
                        computers = []
                        for uuid in menus:
                            if db.isTargetRegister(uuid, P2IT.COMPUTER):
                                logger.debug("computer %s is already registered as a P2IT.COMPUTER"%(uuid))
                                continue
                            menu = menus[uuid]
                            imagingData = {'menu':{uuid:menu}, 'uuid':uuid}
                            computers.append((h_hostnames[uuid], h_macaddress[uuid], imagingData))

                        def treatRegisters(results, uuids = uuids):
                            failures = uuids
                            for l_uuid in results:
                                if l_uuid in failures:
                                    failures.remove(l_uuid)
                            return failures

                        d = i.computersRegister(computers)
                        d.addCallback(treatRegisters)
                        defer_list.append(d)
                    else:
                        logger.error("couldn't initialize the ImagingApi to %s"%(url))
                        db.changeTargetsSynchroState(menus.keys(), P2IT.COMPUTER_IN_PROFILE, P2ISS.TODO)
                        return [False, ""]

                def sendResult(results, pid = pid, db = db):
                    failures = []
                    for fail in results:
                        failures.extend(fail[1])
                    #if failures == False:
                    if len(failures) == 0:
                        db.changeTargetsSynchroState([pid], P2IT.PROFILE, P2ISS.DONE)
                        return [True]
                    db.delProfileMenuTarget(failures)
                    db.changeTargetsSynchroState([pid], P2IT.PROFILE, P2ISS.INIT_ERROR)
                    return [False, failures]
                #if defer_list == False:
                    #if uuids == False: # the profile is empty
                if len(defer_list) == 0:
                    if len(uuids) == 0: # the profile is empty

                        db.changeTargetsSynchroState([pid], P2IT.PROFILE, P2ISS.DONE)
                        return [True]
                    else: # the profile wasn't empty => we fail to treat it
                        db.changeTargetsSynchroState([pid], P2IT.PROFILE, P2ISS.INIT_ERROR)
                        return [False]

                defer_list = defer.DeferredList(defer_list)
                defer_list.addCallback(sendResult)
                return defer_list
        return [True]

    def Windows_Answer_list_File(self,start=0,end=-1):
        """
            returns a list of names (with extension, without full path) of all files
        """
        filexml="/var/lib/pulse2/imaging/postinst/sysprep/"
        if not path.exists(filexml):
            makedirs(filexml, 0722)
        files = []
        osfile = []
        descriptionfile = []
        for name in listdir(filexml):
            absolufile = path.join(filexml, name)
            if name.endswith('.xml') and path.isfile(absolufile):
                files.append(name)
                fichier = open(absolufile,"r")
                for ligne in fichier:
                    if ligne.startswith("OS"):
                        print ligne
                        osfile.append(ligne)
                        break
                else:
                    osfile.append("os missing")
                fichier.close()

                #Do same thing for file notes
                fichier = open(absolufile,"r")
                for ligne in fichier:
                    if ligne.startswith("Notes:"):
                        print ligne
                        descriptionfile.append(ligne[7:-1])
                        break
                else:
                    descriptionfile.append("Missing description")
                fichier.close()
        # create result object
        result = {}
        result['count'] = len(files)
        if end == -1:
            end = result['count']
        result['file'] = files[start:end]
        result['os'] = osfile[start:end]
        result['description'] = descriptionfile[start:end]
        #result['description'] = result['description'][7:-1]
        return result

    def Windows_Answer_File_Generator(self, xmlWAFG, title):
        filexml="/var/lib/pulse2/imaging/postinst/sysprep/"
        filetmp="/tmp/"

        if not path.exists(filexml):
            makedirs(filexml, 0722)

        #test if file already exists
        if path.isfile(filexml+title) :
            try :
                f = open(filetmp+title, 'w')
                f.write(xmlWAFG)
            except Exception, e:
                logging.getLogger().exception(e)
                return False
            else:
                f.close()

            md5tmp = md5file(filetmp+title)
            md5xml = md5file(filexml+title)

            #In this case, compare md5 checksum between filetmp and filexml
            if md5tmp != md5xml :
                #Create new file name
                newTitle = title.split('.')
                newTitle = newTitle[0]
                newTitle = newTitle + '_' + md5tmp+'.xml'
                #Move tmpfile to correct location
                rename(filetmp+title, filexml+newTitle)
                return True

            #Tmpfile is no use anymore
            else :
                remove(filetmp+title)
                return True
        else :
            filexml = filexml + title
            try:
                f = open(filexml, 'w')
                f.write(xmlWAFG)
            except  Exception, e:
                logging.getLogger().exception(e)
                return False
            else:
                f.close()
                return True

    def editWindowsAnswerFile(self, xmlWAFG, title):
        filexml="/var/lib/pulse2/imaging/postinst/sysprep/"

        #test if file already exists
        if path.isfile(filexml+title) :
            try :
                f = open(filexml+title, 'w')
                f.write(xmlWAFG)
            except Exception, e:
                logging.getLogger().exception(e)
                return False
            else:
                f.close()

    def getWindowsAnswerFileParameters(self, filename):
        """
        return the parameters list of sysprep answer file
        """

        filexml = "/var/lib/pulse2/imaging/postinst/sysprep/"
        filexml = filexml + filename

        parameters = ""
        os = ""
        description = ""
        #get information from sysprep file
        try:
            f = open(filexml, "r")
            #get line to add to json object
            for line in f:
                    if line.startswith("OS"):
                        line = line.split(" ")
                        os = " ".join(line[1:3])
                        break

            for line in f:
                    if line.startswith("Notes"):
                        line = line.split(" ")
                        description = " ".join(line[1:])
                        break

            for line in f:
                    if line.startswith("list"):
                        parameters = parameters + line[18:-1]
                        break

            parameters = json.loads(parameters)
            parameters["Os"] = os
            parameters['Notes'] = description
        except Exception, e:
            logging.getLogger().exception(e)
            return False

        else:
            f.close()
            return parameters

    def deleteWindowsAnswerFile(self, title):
        filexml="/var/lib/pulse2/imaging/postinst/sysprep/"
        filexml = filexml + title

        if path.isfile(filexml) :
            remove(filexml)
            return True
        else :
            return False

    def selectWindowsAnswerFile(self, title):
        #"""
        #Return all the content of sysprep answer file named title if exists.
        #"""
        filexml="/var/lib/pulse2/imaging/postinst/sysprep/"
        filexml = filexml + title
        content, content2 = [], []

        if path.isfile(filexml) :
        ##Open file
            try :
                f = open(filexml, 'r')
                #Read file content
                for line in f :
                    content.append(line)

				#search one specific line
                for line in content :
                    if line.startswith("list"):
                        pass
                    else :
                        content2.append(line)

            except Exception, e:
                logging.getLogger().exception(e)
                return False
            else :
                f.close()
            return content2
        else :
            return False

    def getMyMenuComputer(self, uuid):
        """ see getMyMenuTarget """
        return xmlrpcCleanup(self.getMyMenuTarget(uuid, P2IT.COMPUTER))

    def setMyMenuComputer(self, target_uuid, params):
        """ see setMyMenuTarget """
        return xmlrpcCleanup(self.setMyMenuTarget(target_uuid, params, P2IT.COMPUTER))

    def getMyMenuProfile(self, uuid):
        """ see getMyMenuTarget """
        return xmlrpcCleanup(self.getMyMenuTarget(uuid, P2IT.PROFILE))

    def setMyMenuProfile(self, target_uuid, params):
        """ see setMyMenuTarget """
        return xmlrpcCleanup(self.setMyMenuTarget(target_uuid, params, P2IT.PROFILE))

    ###### POST INSTALL SCRIPTS
    def getAllTargetPostInstallScript(self, target_uuid, start = 0, end = -1, filter = ''):
        """
        get the list of all the post install script that are possible for a target

        @param target_uuid: the target's UUID (Target.uuid)
        @type target_uuid: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getAllTargetPostInstallScript(target_uuid, start, end, filter))
        count = db.countAllTargetPostInstallScript(target_uuid, filter)
        return [count, xmlrpcCleanup(ret)]

    def getAllPostInstallScripts(self, location, start = 0, end = -1, filter = ''):
        """
        get the list of all the post install script possible in a location

        @param location: the location uuid (Entity.uuid)
        @type location: str

        @param start: the beginning of the list, default 0
        @type start: int

        @param end: the end of the list, if == -1, no end limit, default -1
        @type end: int

        @param filter: a string to filter the list, default ''
        @type filter: str

        @returns: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        db = ImagingDatabase()
        ret = map(lambda l: l.toH(), db.getAllPostInstallScripts(location, start, end, filter))
        count = db.countAllPostInstallScripts(location, filter)
        return [count, xmlrpcCleanup(ret)]

    def getPostInstallScript(self, pis_uuid, location_id):
        """
        get the detail of a post install script

        @param pis_uuid: the post install script uuid
        @type pis_uuid: str

        @returns: a dict with all the detail of the post install script or False if that pis dont exists
        @rtype: dict
        """
        pis = ImagingDatabase().getPostInstallScript(pis_uuid, None, location_id)
        if pis:
            return xmlrpcCleanup(pis.toH())
        return xmlrpcCleanup(False)

    # edit
    def delPostInstallScript(self, pis_uuid):
        """
        delete a post install script from a location
        it's only possible for pis created after the install

        @param pis_uuid: the post install script uuid
        @type pis_uuid: str

        @returns: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        # TODO should be sync
        try:
            return xmlrpcCleanup(ImagingDatabase().delPostInstallScript(pis_uuid))
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def getComputersWithThisPostInstallScript(self, pis_uuid):
        """
        Get a computer who have a master attached with this postinstall script
        Used to update postinstall script on /var/lib/pulse2/imaging/master/postinst.d/

        @param pis_uuid: postinstall script UUID
        @type pis_uuid: str

        @return: list of Computer UUID
        @rtype: list
        """
        return xmlrpcCleanup(ImagingDatabase().getComputersWithThisPostInstallScript(pis_uuid))

    def editPostInstallScript(self, pis_uuid, params):
        """
        edit a post install script in a location

        @param pis_uuid: the post install script uuid
        @type pis_uuid: str

        @param params: the detail of the post install script
        @type params: dict

        @returns: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        try:
            db = ImagingDatabase()
            res_db = db.editPostInstallScript(pis_uuid, params)
            if res_db:
                computer_uuids = self.getComputersWithThisPostInstallScript(pis_uuid)
                return self.__synchroTargets(computer_uuids, P2IT.COMPUTER)

            return xmlrpcCleanup(res_db)
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def addPostInstallScript(self, loc_id, params):
        """
        add a post install script in a location

        @param loc_id: the location uuid (Entity.uuid)
        @type loc_id: str

        @param params: the detail of the post install script
        @type params: dict

        @returns: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        # TODO should be sync
        try:
            return xmlrpcCleanup(ImagingDatabase().addPostInstallScript(loc_id, params))
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def createBootServiceFromPostInstall(self, script_id, loc_id):
        """
        create a boot service from a postinstall script

        @param script_id: id of the postinstall script
        @type script_id: int

        @param loc_id: the uuid of the location (field Entity.uuid)
        @type loc_id: str

        @return:
        @rtype:
        """

        try:
            # Add entry in BootService Table
            db = ImagingDatabase()
            script_file = db.createBootServiceFromPostInstall(script_id)
            if not script_file:
                raise Exception("Boot service already exists")

            # Create .sh file
            url = chooseImagingApiUrl(loc_id)
            i = ImagingApi(url.encode('utf8')) # TODO why do we need to encode....

            return xmlrpcCleanup(i.createBootServiceFromPostInstall(script_file))
        except Exception, e:
            return xmlrpcCleanup([False, e])

    def __inventory_check(self, MACAddress, waitToBeInventoried, timeout=20):
        """
        Get the computer instance with repeated attempts until timeout
        (GLPI case), otherwise only one attempt processed.

        @param MACAddress: MAC address of computer
        @type MACAddress: str

        @param waitToBeInventoried: If True, a periodic check until timeout
        @type waitToBeInventoried: bool

        @param timeout: timeout of attempts
        @type timeout: int

        @return: machine instance
        @rtype: object
        """
        if waitToBeInventoried :
            start = time.time()

            while True :
                computer = self.__get_computer(MACAddress)
                time.sleep(1)
                if computer :
                    return computer
                if time.time() > (start + timeout) :
                    break
        else :
            return self.__get_computer(MACAddress)


    def __get_computer (self, MACAddress):
        """
        Get the computer from inventory
        @param MACAddress: MAC address of computer
        @type MACAddress: str

        @return: machine instance
        @rtype: object
        """
        uuid = None
        db_computer = ComputerManager().getComputerByMac(MACAddress)
        if db_computer :

            if isinstance(db_computer, dict):
                uuid = db_computer['uuid']
            elif hasattr(db_computer, 'getUUID'):
                uuid = db_computer.getUUID()
            elif hasattr(db_computer, 'uuid'):
                uuid = db_computer.uuid
            if uuid :
                location = ComputerLocationManager().getMachinesLocations([uuid])
                if isinstance(location, dict) :
                    if uuid in location :
                        return db_computer



    ###### API to be called from the imaging server (ie : without authentication)
    def computerRegister(self, imaging_server_uuid, hostname, domain, MACAddress, profile, entity = None, waitToBeInventoried=False):
        """
        Called by the Package Server to register a new computer.
        The computer name may contain a profile and an entity path (like profile:/entityA/entityB/computer)

        @param imaging_server_uuid:
        @type imaging_server_uuid:

        @param hostname: the computer to be registered hostname
        @type hostname: str

        @param domain: the computer to be registered domain
        @type domain: str

        @param MACAddress: the computer to be registered mac address
        @type MACAddress: str

        @param profile: the computer to be registered profile
        @type profile: str

        @param entity: the computer to be registered entity
        @type entity:

        @returns: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
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
        imaging_server = imaging_server[0]

        p = None
        if entity:
            entity_name = entity
            # get the entity UUID
            entities_uuid = ComputerLocationManager().getLocationsFromPathString([entity_name])
            entity_uuid = entities_uuid[0]
            if not entity_uuid:
                return [False, "The entity %s doesn't exists" % entity_name]
            else:
                loc_id = entity_uuid
                imaging_server = db.getImagingServerByEntityUUID(loc_id)
        if profile != '':
            # if entities: we need to get the profile from this entity!
            # we have to register as a profile element
            is_uuid = imaging_server.getUUID()
            if not is_uuid:
                return [False, "Failed to find the correct profile (%s) in %s"%(profile, imaging_server_uuid)]
            p = ComputerProfileManager().getProfileByNameImagingServer(profile, is_uuid)
            if type(p) == list:
                if len(p) != 1:
                    return [False, "Failed to find the correct profile (%s) in %s"%(profile, imaging_server_uuid)]
                p = p[0]

        computer = {
            'computername': hostname, # FIXME : what about domain ?
            'computerdescription': '',
            'computerip': '',
            'computermac': MACAddress,
            'computernet': '',
            'operating_system': 'Unknown operating system (PXE network boot inventory)',
            'location_uuid': loc_id}

        uuid = None
        db_computer = self.__inventory_check(MACAddress, waitToBeInventoried)
        if db_computer != None:
            db_computer_name = ''
            if type(db_computer) == dict:
                uuid = db_computer['uuid']
                if 'hostname' in db_computer:
                    db_computer_name = db_computer['hostname']
                elif 'name' in db_computer:
                    db_computer_name = db_computer['name']
            elif hasattr(db_computer, 'getUUID'):
                uuid = db_computer.getUUID()
                db_computer_name = db_computer.name
            elif hasattr(db_computer, 'uuid'):
                uuid = db_computer.uuid
                db_computer_name = db_computer.name
            if db_computer_name.lower() != hostname.lower():
                # Computer added via OCS -> renamed by PXE entry
                renamed = ComputerManager().editComputerName(self.currentContext, uuid, hostname)
                if renamed :
                     logger.info("Machine '%s' renamed to '%s'."% (db_computer_name, hostname))
                else :
                     logger.warning("Machine '%s' couldn't be renamed to '%s'."% (db_computer_name, hostname))


        # If a computer with this name already exists, check that the MAC
        # address is also matching
        ctx = self.currentContext
        if uuid :
            # Get list of mac of uuid:
            # dict of computer with their MAC Addresses ({'UUIDX': ['MAC1', 'MAC2']})
            db_computer = ComputerManager().getMachineMac(ctx, {'uuid': uuid})

        if db_computer:
            if len(db_computer) > 1:
                err = "More than one computer in database with hostname %s. Aborting !" % hostname
                logger.error(err)
                return [False, err]
            else:
                # Checking if MAC address match
                if uuid:
                    macs = [x.lower() for x in db_computer[uuid] if x is not None]
                else:
                    macs = []
                logger.debug("A computer (uuid = %s) with a corresponding hostname already exists in the database, checking its MAC addresses" % uuid)
                hasMAC = False
                if not macs:
                    # No MAC address ? We consider we have a match
                    logger.warn('Merging computer %s with already existing %s without checking its MAC address (empty MAC address list returned)' % (hostname, uuid))
                    hasMAC = True
                elif MACAddress.lower() in macs:
                    hasMAC = True
                if not hasMAC:
                    err = "A computer (uuid = %s) with this hostname already exists, but the MAC address doesn't match: %s not in %s" % (uuid, MACAddress, macs)
                    logger.error(err)
                    return [False, err]
                else:
                    logger.debug("The computer (uuid = %s) is matching with its hostname and one of its MAC addresses (%s)" % (uuid, MACAddress))

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
            logger.debug("computer %s (%s) already exists, we don't need to declare it again" % (hostname, MACAddress))

        target_type = P2IT.COMPUTER
        is_registrated = db.isTargetRegister(uuid, target_type)

        def sendResult(results, uuid): return [True, uuid]

        if not is_registrated and p == None:
            logger.info("Registering computer %s (%s) in imaging module" % (hostname, MACAddress))
            params = {
                'target_name': hostname,
            }
            # Set the computer menu
            try:
                db.setMyMenuTarget(uuid, params, target_type) # FIXME : are not we supposed to deal with the return value ?
            except Exception, e:
                return xmlrpcCleanup([False, str(e)])
            # Tell the MMC agent to synchronize the menu
            # As it in some way returns a deferred object, it is run in
            # background
            d = self.synchroComputer(uuid, mac = MACAddress)
            d.addCallback(sendResult, uuid)
        elif not is_registrated:
            is_pregistrated = db.isTargetRegister(p.getUUID(), P2IT.PROFILE)
            if not is_pregistrated:
                logger.error("profile %s don't exists in %s or is not registerd in imaging"%(profile, imaging_server_uuid))
                return [False, "profile %s don't exists in %s or is not registerd in imaging"%(profile, imaging_server_uuid)]

            logger.info("computer %s (%s) needs to be registered in the profile %s" % (hostname, MACAddress, profile))

            def treatAddComputersToProfile(result, uuid = uuid, hostname = hostname, MACAddress = MACAddress, profile = profile):
                if not result:
                    logger.error("failed to put the computer %s (%s) in the profile %s" % (hostname, MACAddress, profile))
                    return defer.fail("failed to put the computer %s (%s) in the profile %s" % (hostname, MACAddress, profile))
                d = self.synchroComputer(uuid)
                d.addCallback(sendResult, uuid)
                return d
            d = ComputerProfileManager().addComputersToProfile(ctx, {uuid:{'uuid':uuid, 'hostname':hostname}}, p.getUUID())
            d.addCallback(treatAddComputersToProfile)
        else:
            logger.debug("computer %s (%s) dont need registration" % (hostname, MACAddress))
            # Synchronize menu
            d = self.synchroComputer(uuid)
            d.addCallback(sendResult, uuid)
        return d

    def imagingServerRegister(self, name, url, uuid):
        """
        Called by the imagingServer register script, it fills all the required fields for an
        imaging server, then the server is available in the list of server not linked to any entity
        and need to be linked.

        @param name: the imaging server name
        @type name: str

        @param url: the url to contact this imaging server
        @type url: str

        @param uuid: the imaging server's uuid (it's generated on the imaging server side)
        @type uuid: str

        @returns: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        db = ImagingDatabase()
        if db.countImagingServerByPackageServerUUID(uuid) != 0:
            return [False, "Already existing UUID: %s" % (uuid)]
        db.registerImagingServer(name, url, uuid)
        return [True, "Your Imaging Server has been correctly registered. You can now associate it to the correct entity in the MMC."]

    def isImagingServerRegistered(self, uuid):
        """
        Return True if the given uuid is already registered for an imaging server,
        False otherwise.

        @param uuid: an imaging server uuid
        @type uuid: str

        @returns: True or False
        @rtype: boolean
        """
        db = ImagingDatabase()
        return db.countImagingServerByPackageServerUUID(uuid)<>0

    def getComputerByMac(self, mac):
        """
        Called by the package server, to obtain a computer UUID/shortname/fqdn in exchange of its MAC address

        @param mac: the mac address
        @type mac: str

        @results: a pair:
            * True if succeed or False otherwise
            * the error in case of failure else the computer as a dict
        @rtype: list
        """
        assert pulse2.utils.isMACAddress(mac)
        db_computer = ComputerManager().getComputerByMac(mac)
        if not db_computer:
            return [False, "imaging.getComputerByMac() : I was unable to find a computer corresponding to the MAC address %s" % mac]

        if type(db_computer) == dict:
            uuid = db_computer['uuid']
            if 'hostname' in db_computer:
                db_computer_name = db_computer['hostname']
            elif 'name' in db_computer:
                db_computer_name = db_computer['name']
        elif hasattr(db_computer, 'getUUID'):
            uuid = db_computer.getUUID()
            db_computer_name = db_computer.name
        elif hasattr(db_computer, 'uuid'):
            uuid = db_computer.uuid
            db_computer_name = db_computer.name
        else:
            return [False, "imaging.getComputerByMac() : I was unable to find the good informations about the computer having %s as a mac address" % mac]

        # Get the entity of the computer
        locations = ComputerLocationManager().getMachinesLocations([uuid])
        entity = ""
        entity_name = ""
        if uuid in locations:
            entity = locations[uuid]
        if entity:
            if 'Label' in entity :
                entity_name = entity['Label']
            # TODO - temporary GLPI hack
            elif 'completename' in entity :
                entity_name = entity['completename']


        return [True, {'uuid': uuid, 'mac': mac, 'shortname': db_computer_name, 'fqdn': db_computer_name, 'entity': entity_name}]

    def getComputerByUUID(self, uuid):
        """
        Called by the package server, to obtain a computer MAC/shortname/fqdn in exchange of uuid

        @param uuid: the computer uuid
        @type uuid: str

        @results: a pair:
            * True if succeed or False otherwise
            * the error in case of failure else the computer as a dict
        @rtype: list
        """
        assert pulse2.utils.isUUID(uuid)
        ctx = self.currentContext
        db_computer = ComputerManager().getComputer(ctx, {'uuid': uuid})
        if not db_computer:
            return [False, "imaging.getComputerByUUID() : I was unable to find a computer corresponding to the UUID %s" % uuid]

        if type(db_computer) == dict:
            uuid = db_computer['uuid']
            if 'hostname' in db_computer:
                db_computer_name = db_computer['hostname']
            elif 'name' in db_computer:
                db_computer_name = db_computer['name']
        elif hasattr(db_computer, 'getUUID'):
            uuid = db_computer.getUUID()
            db_computer_name = db_computer.name
        elif hasattr(db_computer, 'uuid'):
            uuid = db_computer.uuid
            db_computer_name = db_computer.name
        else:
            return [False, "imaging.getComputerByUUID() : I was unable to find the good informations about the computer having %s as UUID" % uuid]
        return [True, {'uuid': uuid, 'mac': db_computer['MACAddress'], 'shortname': db_computer_name, 'fqdn': db_computer_name}]

    def logClientAction(self, imaging_server_uuid, computer_uuid, level, phase, message):
        """
        Called by the package server, to log some info on imaging
        like backup/restore start or finish, in which state....

        @param imaging_server_uuid: the imaging server uuid where the action happened
        @type imaging_server_uuid: str

        @param computer_uuid: the computer on which the action happened
        @type computer_uuid: str

        @param level: the level of the message
        @type level: str

        @param phase: in which phase that happened (the id of ImagingLogState)
        @type phase: int

        @param message: the textual message
        @type message: str

        @results: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        logger = logging.getLogger()
        log = {
            'level': level,
            'detail': message,
            'state': phase}
        db = ImagingDatabase()
        if db.countImagingServerByPackageServerUUID(imaging_server_uuid) == 0:
            return [False, "The imaging server UUID you try to access doesn't exist in the imaging database."]
        if not db.isTargetRegister(computer_uuid, P2IT.COMPUTER) \
           and not db.isTargetRegister(computer_uuid, P2IT.COMPUTER_IN_PROFILE):
            return [False, "The computer UUID you try to access doesn't exists in the imaging database."]

        try:
            ret = db.logClientAction(imaging_server_uuid, computer_uuid, log)
            ret = [ret, '']
        except Exception, e:
            logger.exception(e)
            ret = [False, str(e)]
        return ret

    def imageRegister(self, imaging_server_uuid, computer_uuid, image_uuid, is_master, name, desc, path, size, creation_date, creator='root', state='UNKNOWN'):
        """
        Called by the Package Server to register a new Image.

        @param imaging_server_uuid: the imaging server uuid where the action happened
        @type imaging_server_uuid: str

        @param computer_uuid: the computer on which the action happened
        @type computer_uuid: str

        @param image_uuid: the image uuid (generated by the imaging server)
        @type image_uuid: str

        @param is_master: is the image a master or an image
        @type is_master: boolean

        @results: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
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
            'creator': creator,
            'state': state}
        db = ImagingDatabase()

        if db.countImagingServerByPackageServerUUID(imaging_server_uuid) == 0:
            return [False, "The imaging server UUID you try to access doesn't exist in the imaging database."]

        if not db.isTargetRegister(computer_uuid, P2IT.COMPUTER) \
           and not db.isTargetRegister(computer_uuid, P2IT.COMPUTER_IN_PROFILE):
            return [False, "The computer UUID (%s) you try to access doesn't exists in the imaging database." % computer_uuid]

        try:
            ret = db.registerImage(imaging_server_uuid, computer_uuid, image)
            ret = [ret, '']
        except Exception, e:
            logging.getLogger().exception(e)
            ret = [False, str(e)]
        return ret

    def imageUpdate(self, imaging_server_uuid, computer_uuid, image_uuid, name, desc, size, update_date, state='UNKNOWN'):
        """
        Called by the Package Server to update an already existing Image.

        @param imaging_server_uuid: the imaging server uuid where the action happened
        @type imaging_server_uuid: str

        @param computer_uuid: the computer on which the action happened
        @type computer_uuid: str

        @param image_uuid: the image uuid (generated by the imaging server)
        @type image_uuid: str

        @results: a pair:
            * True if succeed or False otherwise
            * the error in case of failure
        @rtype: list
        """
        image = {
            'name': name,
            'desc': desc,
            'uuid': image_uuid,
            'checksum': '',
            'size': int(size),
            'update_date': update_date,
            'state': state}
        db = ImagingDatabase()

        if db.countImagingServerByPackageServerUUID(imaging_server_uuid) == 0:
            return [False, "The imaging server %s you try to access doesn't exist in the imaging database." % imaging_server_uuid]

        if not db.isTargetRegister(computer_uuid, P2IT.COMPUTER) \
           and not db.isTargetRegister(computer_uuid, P2IT.COMPUTER_IN_PROFILE):
            return [False, "The computer %s you try to access doesn't exists in the imaging database." % computer_uuid]

        item_uuid = db.getImageUUIDFromImageUUID(image_uuid)
        if not item_uuid:
            return [False, "The image %s you try to access doesn't exists in the imaging database." % image_uuid]

        try:
            ret = db.editImage(item_uuid, image)
            ret = [ret, '']
        except Exception, e:
            logging.getLogger().exception(e)
            ret = [False, str(e)]
        return ret

    def injectInventory(self, imaging_server_uuid, computer_uuid, inventory):
        """
        Called by the Package Server to inject an inventory.
        """
        db = ImagingDatabase()
        try:
            ret = db.injectInventory(imaging_server_uuid, computer_uuid, inventory)
        except Exception, e:
            logging.getLogger().exception(e)
            ret = [False, str(e)]
        return ret

    def getPartitionsToBackupRestore(self, computer_uuid):
        """
        Called by the web interface to get the computer disks and partitions
        to backup and restore.
        """
        return ImagingDatabase().getPartitionsToBackupRestore(computer_uuid)


    def getPXEParams(self, imaging_server_uuid):
        """
        Called by the Package Server to get the PXE Password and keymap
        """
        location = ImagingDatabase().getImagingServerEntity(imaging_server_uuid)
        if location == None:
            # Package server has not been registered, we return an empty menu
            return {}
        params = {}
        params['pxe_keymap'] = location.pxe_keymap
        params['pxe_password'] = location.pxe_password
        return xmlrpcCleanup(params)


    def getClonezillaParamsForTarget(self, computer_uuid):
        """
        Called by davos to get Clonezilla parameters for a machine.
        Get Clonezilla parameters first for the machine itself and if not
        defined, get the parameters set at the server level

        @param computer_uuid: the computer on which the action is happening
        @type computer_uuid: str

        @results: clonezilla parameters
        @rtype: dict
        """
        db = ImagingDatabase()
        logger = logging.getLogger()
        params = {}
        # First find clonezilla parameters for the machine itself
        # TBD
        params['clonezilla_saver_params'] = ''
        params['clonezilla_restorer_params'] = ''
        # End TBD
        # If the parameters have not been set for the machine, get the
        # parameters at entity level
        if params['clonezilla_saver_params'] == '' or params['clonezilla_restorer_params'] == '':
            location_uuid = db.getProfileLocation(computer_uuid)
            logger.info('Asking for Clonezilla parameters set for entity %s', location_uuid)
            if params['clonezilla_saver_params'] == '':
                params['clonezilla_saver_params'] = db.getClonezillaSaverParams(location_uuid)
                logger.info('Found saver parameters: %s', params['clonezilla_saver_params'])
            if params['clonezilla_restorer_params'] == '':
                params['clonezilla_restorer_params'] = db.getClonezillaRestorerParams(location_uuid)
                logger.info('Found restorer parameters: %s', params['clonezilla_restorer_params'])
        return xmlrpcCleanup(params)


    def getDefaultMenuForRegistering(self, imaging_server_uuid):
        """
        Called by the Package Server to get the default menu used by computers
        to subscribe from the database.

        @param imaging_server_uuid: the uuid of the calling imaging server
        @type imaging_server_uuid: str

        @results: give the default menu for subscription (Menu.id == 2)
        @rtype: dict
        """
        db = ImagingDatabase()
        logger = logging.getLogger()
        menu = self.__generateDefaultSuscribeMenu(logger, db, imaging_server_uuid)
        return xmlrpcCleanup(menu)

    def computerChangeDefaultMenuItem(self, imaging_server_uuid, computer_uuid, item_number):
        """
        Called by the Package Server to change the default value of a menu

        @param imaging_server_uuid: the uuid of the calling imaging serve
        @type imaging_server_uuid: str

        @param computer_uuid:
        @type computer_uuid: str

        @param item_number:
        @type item_number: int

        @results: couple of : a boolean saying if it succeed and the error message
        @rtype: list
        """
        db = ImagingDatabase()
        try:
            if type(item_number) != int:
                try:
                    item_number = int(item_number)
                except:
                    pass
            db.computerChangeDefaultMenuItem(imaging_server_uuid, computer_uuid, item_number)

            # need to send back the menu to the package server
            profile = ComputerProfileManager().getComputersProfile(computer_uuid)
            if profile != None:
                self.__synchroTargets([computer_uuid], P2IT.COMPUTER_IN_PROFILE)
            else:
                self.__synchroTargets([computer_uuid], P2IT.COMPUTER)

        except Exception, e:
            logging.getLogger().exception(e)
            return [False, str(e)]
        return [True, True]

def chooseMacAddress(ctx, uuid, macs):
    # should pass uuids and the list of uuids
    nets = getComputersNetwork_filtered(ctx, {'uuid':uuid})
    nets = nets[0][1]

    # For nic_uuid variable, get Target Nic UUID from Target table
    # It's buggy... If Target is not registered, we will never
    # find corresponding target's Nic_uuid
    nic_uuid = ImagingDatabase().getTargetNICuuid(uuid)

    # So, if Target have only one Mac address, and this one is part
    # of the macs list, return this
    if len(nets['macAddress']) == 1:
        mac = nets['macAddress'][0]
        if mac in macs:
            return mac

    if len(nic_uuid) != 1:
        logging.getLogger().error("couldn't find the registered mac address for computer %s"%uuid)
        return None

    # If target has more than one macadresses, choose the one registered
    # in imaging module (current target must be registered to find one)
    nic_uuid = nic_uuid[0]
    mac = None
    for i in range(0, len(nets['macAddress'])):
        if nets['networkUuids'][i] == nic_uuid:
            mac = nets['macAddress'][i]
    if mac == None:
        logging.getLogger().error("couldn't find the registered mac address for computer %s"%uuid)
    return mac

def getJustOneMacPerComputer(ctx, macs):
    """
    @param: dict of computers with their MAC Addresses ({'UUIDX': ['MAC1', 'MAC2']})
    @return: dict of computers with only one MAC Address ({'UUIDX': 'MAC1'})
    @raises: TypeError if macs is not a dict
    ...
    """
    if type(macs) == dict:
        ret = {}
        for uuid in macs:
            macs_list = macs[uuid]
            # Get an unique list of MACs
            macs_list = list(set(macs_list))
            if len(macs_list) != 1:
                mac = chooseMacAddress(ctx, uuid, macs_list)
                if mac:
                    ret[uuid] = mac
                else:
                    # If the computer is not registered in imaging
                    # return an empty string
                    ret[uuid] = ''
            else:
                ret[uuid] = macs_list[0]
        return ret
    else:
        raise TypeError("Invalid parameter: %s" % macs)

def synchroComputers(ctx, uuids, ctype = P2IT.COMPUTER):
    """ see __synchroTargets """
    ret = synchroTargets(ctx, uuids, ctype)
    return xmlrpcCleanup(ret)

def synchroTargets(ctx, uuids, target_type, macs = {}, wol = False):
    """
    synchronize boot menus
    @param uuids: list of computers UUIDS
    @type uuids: list

    @param target_type: Pulse imaging type (P2IT COMPUTER, PROFILE, ...)
    @type target_type: int

    @param macs: Dict with computer UUID as key, imaging MAC as value ({'UUIDXXX': 'xx:xx:xx:xx:xx:xx'})
    @type macs: dict

    @param wol: WOL bootmenu will be set or not
    @type wol: bool

    @return: Deferred list
    @rtype: defer_list
    """

    # initialize stuff
    logger = logging.getLogger()
    db = ImagingDatabase()

    # store the fact that we are attempting a sync
    db.changeTargetsSynchroState(uuids, target_type, P2ISS.RUNNING)
    # Load up l_uuids with the required info (computer within profile OR given computers)
    if target_type == P2IT.PROFILE:
        pid = uuids[0]
        l_uuids = map(lambda c: c.uuid, ComputerProfileManager().getProfileContent(pid))
    else:
        pid = None
        l_uuids = uuids

    # give up if it appears that no menu as to be synced
    if l_uuids == False:
        db.changeTargetsSynchroState(uuids, target_type, P2ISS.DONE)
        return [True]

    # gather the required menus
    distinct_loc = generateMenus(logger, db, l_uuids)

    defer_list = []
    h_computers = {}
    registered = db.isTargetRegisterInPackageServer(l_uuids, P2IT.ALL_COMPUTERS)

    # loop over each return location
    for loc_uuid in distinct_loc:
        # extract menus and url for our location
        (url, menus) = distinct_loc[loc_uuid][0:2]

        # If wol is True, generated bootmenu is the WOL one
        if wol:
            for uuid in menus:
                menus[uuid]['default_item'] = menus[uuid]['default_item_WOL']

        # store into to_register the list of menus to register
        to_register = {}
        for uuid in menus:
            if not registered[uuid]:
                to_register[uuid] = menus[uuid]

        # drop location processing if there is no menu to register
        #if to_register.keys() == False:
        if len(to_register.keys()) == 0:
            continue

        # store into h_hostnames hostnames of computers to register
        h_hostnames = {}
        hostnames = ComputerManager().getMachineHostname(ctx, {'uuids' : to_register.keys()})
        if type(hostnames) == list:
            for computer in hostnames:
                h_hostnames[computer['uuid']] = computer['hostname']
        else:
            h_hostnames[hostnames['uuid']] = hostnames['hostname']

        # store into h_macaddress the MAC addr of computers to register
        if macs:
            h_macaddress = macs
        else:
            h_macaddress = getJustOneMacPerComputer(ctx, ComputerManager().getMachineMac(ctx, {'uuids' : to_register.keys()}))

        # then try to build a list of computer with menus, hostname, mac addr and so on
        computers = []
        for uuid in to_register:
            if db.isTargetRegister(uuid, P2IT.COMPUTER):
                logger.debug("computer %s is already registered as a P2IT.COMPUTER" % (uuid))
            menu = menus[uuid]
            imagingData = {'menu' : {uuid : menu}, 'uuid' : uuid}

            if not uuid in h_macaddress:
                logger.warn("synchroTargets() : computer %s do not have a MAC address" % (uuid))
                continue

            mac = h_macaddress[uuid]
            if (type(mac) == list or type(mac) == tuple) and len(mac) == 1:
                mac = mac[0]
                if (type(mac) == list or type(mac) == tuple) and len(mac) == 1:
                    mac = mac[0]
            if uuid in h_hostnames :
                computers.append((h_hostnames[uuid], mac, imagingData))

        if not url in h_computers:
            h_computers[url] = []
        h_computers[url].extend(computers)

    # if there are some new computers in the profile, register them
    #if h_computers.keys():
    if len(h_computers.keys()) != 0:
        for url in h_computers:
            computers = h_computers[url]
            i = ImagingApi(url.encode('utf8')) # TODO why do we need to encode....
            if i != None:
                def treatRegister(results, uuids = to_register.keys(), logger = logger, url = url):
                    if type(results) == list and len(results) > 0 and  results[0] == 'PULSE2_ERR':
                        logger.warn("couldn't connect to the ImagingApi %s"%(url))
                        return uuids
                    failures = uuids
                    for l_uuid in results:
                        db.setTargetRegisteredInPackageServer(l_uuid, P2IT.ALL_COMPUTERS)
                        if l_uuid in failures:
                            failures.remove(l_uuid)
                    return failures

                d = i.computersRegister(computers)
                d.addCallback(treatRegister)
                defer_list.append(d)
            else:
                logger.error("couldn't initialize the ImagingApi to %s"%(url))

    distinct_loc = xmlrpcCleanup(distinct_loc)
    #if defer_list == False:
    if len(defer_list) == 0:
        distinct_locs = distinct_loc
        keyvaleur = distinct_loc.keys()
        return synchroTargetsSecondPart(ctx, distinct_locs, target_type, pid, macs = macs)
    else:
        def sendResult(results, distinct_loc = distinct_loc, target_type = target_type, pid = pid, db = db):
            for result, uuids in results:
                db.delProfileMenuTarget(uuids)
            distinct_locs = distinct_loc
            keyvaleur = distinct_loc.keys()
            return synchroTargetsSecondPart(ctx, distinct_locs, target_type, pid, macs = macs)
        defer_list = defer.DeferredList(defer_list)
        defer_list.addCallback(sendResult)
        return defer_list

def synchroTargetsSecondPart(ctx, distinct_loc, target_type, pid, macs = {}):
    logger = logging.getLogger()
    db = ImagingDatabase()
    def treatFailures(result, location_uuid, url, distinct_loc = distinct_loc, logger = logger, target_type = target_type, pid = pid, db = db):
        failures = []
        success = []
        if type(result) == list and len(result) > 0 and result[0] == 'PULSE2_ERR':
            logger.warn("couldn't connect to the ImagingApi %s"%(url))
        else:
            for uuid in result:
                logger.debug("succeed to synchronize menu for %s"%(str(uuid)))
                success.append(uuid)

        for uuid in distinct_loc[location_uuid][1]:
            if not uuid in success:
                logger.warn("failed to synchronize menu for %s"%(str(uuid)))
                failures.append(uuid)

        if pid != None:
            #if failures:
            if len(failures) != 0:
                db.changeTargetsSynchroState([pid], target_type, P2ISS.TODO)
            else:
                db.changeTargetsSynchroState([pid], target_type, P2ISS.DONE)
        else:
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
        macaddresses = macs and macs or getJustOneMacPerComputer(ctx, ComputerManager().getMachineMac(ctx, {'uuids' : l_menus.keys()}))

        for uuid in l_menus.keys():
            l_menus[uuid]['target']['macaddress'] = macaddresses[uuid]

        d = i.computersMenuSet(l_menus)
        d.addCallback(treatFailures, location_uuid, url)
        dl.append(d)

    def sendResult(results):
        failures = []
        for s, uuids in results:
            failures.extend(uuids)
        #if failures == False:
        if len(failures) == 0:
            return [True]
        return [False, failures]

    dl = defer.DeferredList(dl)
    dl.addCallback(sendResult)
    return dl

###### GET IMAGING API URL
def chooseImagingApiUrl(location):
    return ImagingDatabase().getEntityUrl(location)


def generateMenusContent(menu, menu_items, loc_uuid, target_uuid = None, h_pis = {}):
    menu['bootservices'] = {}
    menu['images'] = {}
    for mi in menu_items:
        if menu['fk_default_item'] == mi.id:
            if 'image' in dir(mi):
                menu['default_item'] = mi.image.name
            else:
                menu['default_item'] = mi.boot_service.default_name
        if menu['fk_default_item_WOL'] == mi.id:
            if 'image' in dir(mi):
                menu['default_item_WOL'] = mi.image.name
            else:
                menu['default_item_WOL'] = mi.boot_service.default_name
        mi = mi.toH()
        if 'image' in mi:
            if mi['image']['id'] in h_pis:
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
    # when no default mi has been defined we take the first element of the menu
    if not menu.has_key('default_item') or menu['default_item'] == None:
    #if not 'default_item' in menu or menu['default_item'] == None:
        menu['default_item'] = 0
    if not menu.has_key('default_item_WOL') or menu['default_item_WOL'] == None:
    #if not 'default_item_WOL' in menu or menu['default_item_WOL'] == None:
        menu['default_item_WOL'] = 0
    return (menu, menu_items, h_pis)


def generateMenus(logger, db, uuids, unique=False):
    logger = logging.getLogger()
    logger.debug("generateMenus for %s"%(str(uuids)))
    # get target location
    distinct_loc = {}

    locations = ComputerLocationManager().getMachinesLocations(uuids)
    if len(locations.keys()) != len(uuids):
        # do fail
        logger.error("couldn't get the target entity for %s"%(str(uuids)))
    h_pis = {}

    targets = db.getTargetsByUUID(uuids)
    h_targets = {}
    for target in targets:
        h_targets[target.uuid] = target.toH()

    for m_uuid in locations:
        if 'uuid' in locations[m_uuid]:
            loc_uuid = locations[m_uuid]['uuid']
        else:
            loc_uuid = "UUID%s"%locations[m_uuid]['id']
        menu_items = db.getBootMenu(m_uuid, P2IT.COMPUTER, 0, -1, '')
        profile = ComputerProfileManager().getComputersProfile(m_uuid)
        logger.debug("computer %s"%(m_uuid))
        if profile != None:
            logger.debug("\tis in profile %s"%(str(profile.id)))
            menu = db.getTargetsMenuTUUID(profile.id)
        else:
            menu = db.getTargetsMenuTUUID(m_uuid)
        menu = menu.toH()
        menu['target'] = h_targets[m_uuid]
        menu, menu_items, h_pis = generateMenusContent(menu, menu_items, loc_uuid, m_uuid, h_pis)

        if loc_uuid in distinct_loc:
            distinct_loc[loc_uuid][1][m_uuid] = menu
        else:
            url = chooseImagingApiUrl(loc_uuid)
            distinct_loc[loc_uuid] = [url, {m_uuid:menu}]

    ims = h_pis.keys()
    for loc_uuid in distinct_loc:
        a_pis = db.getImagesPostInstallScript(ims, None, loc_uuid)
        for pis, im, name_i18n, desc_i18n, pis_order in a_pis:
            name = pis.default_name
            desc = pis.default_desc
            if name_i18n != None:
                name = name_i18n.label
            if desc_i18n != None:
                desc = desc_i18n.label

            pis = {
                'id':pis.id,
                'name':name,
                'desc':desc,
                'value':pis.value,
                'order':pis_order
            }
            a_targets = h_pis[im.id]
            for loc_uuid, t_uuid, order in a_targets:
                if not distinct_loc[loc_uuid][1][t_uuid]['images'][order].has_key('post_install_script'):
                #if not 'post_install_script' in distinct_loc[loc_uuid][1][t_uuid]['images'][order]:
                    distinct_loc[loc_uuid][1][t_uuid]['images'][order]['post_install_script'] = []
                distinct_loc[loc_uuid][1][t_uuid]['images'][order]['post_install_script'].append(pis)
    if unique:
        return distinct_loc.values()[0][1].values()[0]
    else:
        return distinct_loc


def computersUnregister(computers_UUID, backup):
    """
    unregister all the computers from the list

    remove a computer from imaging means :
     * ask the imaging server to remove the computer's menu
     * ask the imaging server to remove all it's images (not the masters)
     * remove the images from the database (Image/ImageOnImagingServer/...)
     * remove the machine from the database (Target/Menu/...)
     * synchronize the target (ie : if the computer is also in the profile,
     it now get the profile menu)

    """
    db = ImagingDatabase()
    logger = logging.getLogger()

    # get the computers
    ret = db.isTargetRegister(computers_UUID, P2IT.ALL_COMPUTERS)
    for uuid in ret:
        if not ret[uuid]:
            logger.info("%s is not registered, it can't be unregistered" % uuid)
            try:
                computers_UUID.pop(computers_UUID.index(uuid))
            except ValueError:
                pass

    # send a request to the pserver to unregister them
    location = db.getTargetsEntity(computers_UUID)

    h_location = {}
    for en, target in location:
        en_uuid = en.uuid
        #if not en_uuid in h_location:
        if not h_location.has_key(en_uuid):
            h_location[en_uuid] = [en, []]
        h_location[en_uuid][1].append(target)

    def treatUnregister(results, uuid, *attr):
        return [results, uuid]


    dl = []
    for en_uuid in h_location:
        (en, targets) = h_location[en_uuid]

        url = chooseImagingApiUrl(en_uuid)
        i = ImagingApi(url.encode('utf8')) # TODO why do we need to encode....

        db = ImagingDatabase()

        if i != None:
            for computer in targets:
                computerUUID = computer.uuid
                # get the list of image uuid

                imageList = []
                # Unregister Targets from DB
                imageList = db.unregisterTargets(computerUUID)
                d = i.computerUnregister(computerUUID, imageList, backup)
                d.addCallback(treatUnregister, computerUUID)
                dl.append(d)
        else:
            logger.info("couldn't initialize the ImagingApi to %s"%(url))

        defer_list = defer.DeferredList(dl)
        return defer_list
    return False

def getComputersNetwork_filtered(ctx, params):
    """
    @return: the computer network information but excludes
    ipv6, empty macs, lo interface and if there is a preferred network
    choose it
    """
    network_data = ComputerManager().getComputersNetwork(ctx, params)
    for interfacelist in network_data:
        datalistip =[]
        indexdel=[]
        listip = interfacelist[1]['ipHostNumber']
        for indexlist,ipstring in enumerate(listip):
            if not ipstring in datalistip:
                datalistip.append(ipstring)
            else:
                indexdel.append(indexlist)
        indexdel.reverse()
        for indexlist in indexdel:
            del interfacelist[1]['ipHostNumber'][indexlist]
            del interfacelist[1]['networkUuids'][indexlist]
            del interfacelist[1]['macAddress'][indexlist]
            del interfacelist[1]['domain'][indexlist]
            del interfacelist[1]['subnetMask'][indexlist]
    for m in xrange(len(network_data)):
        cpt_data = network_data[m][1]
        ipHostNumber = []
        macAddress = []
        networkUuids = []
        subnetMask = []
        domainlist = []
        for i in xrange(len(cpt_data['ipHostNumber'])):
            ip = cpt_data['ipHostNumber'][i]
            mac = cpt_data['macAddress'][i]
            uuid = cpt_data['networkUuids'][i]
            netmask = cpt_data['subnetMask'][i]
            domain = cpt_data['domain'][i]
            # IP filtering
            if not ip or ip == '127.0.0.1':
                continue
            if not mac:
                continue
            if not is_ipv4_valid(ip):
                continue
            domainlist.append(domain)
            ipHostNumber.append(ip)
            macAddress.append(mac)
            networkUuids.append(uuid)
            subnetMask.append(netmask)
        # If there is more than one address, apply preferred netowrk algo
        preferred_network = ImagingConfig().preferred_network
        if len(macAddress) > 1 and preferred_network:
           for i in xrange(len(macAddress)):
               ip = ipHostNumber[i]
               if ipaddr.IPAddress(ip) in ipaddr.IPNetwork(preferred_network):
                   ipHostNumber = [ip]
                   macAddress = [macAddress[i]]
                   networkUuids = [networkUuids[i]]
                   subnetMask = [subnetMask[i]]
                   domainlist = [domainlist[i]]
                   break
        network_data[m][1]['ipHostNumber'] = ipHostNumber
        network_data[m][1]['macAddress'] = macAddress
        network_data[m][1]['networkUuids'] = networkUuids
        network_data[m][1]['subnetMask'] = subnetMask
        network_data[m][1]['domain'] = domainlist
    return network_data

def getMachineMac_filtered(ctx, params):
    net_data = getComputersNetwork_filtered(ctx, params)
    return [{x[1]['objectUUID'][0]:x[1]['macAddress']} for x in net_data]

def hasMoreThanOneEthCard(ctx, uuids):
    net_data = getComputersNetwork_filtered(ctx, {'uuids': uuids})
    return [x[1]['objectUUID'][0] for x in net_data if len(x[1]['macAddress'])>1]
