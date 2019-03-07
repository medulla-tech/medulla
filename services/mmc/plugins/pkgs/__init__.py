# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva
# (c) 2017      Siveo
#
# $Id$
#
# This file is part of MMC.
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
import os
from os.path import basename
import shutil
import requests
import json
import tempfile
import urllib2
import re
from contextlib import closing
from ConfigParser import ConfigParser
from base64 import b64encode, b64decode
from time import time
from json import loads as parse_json
import subprocess
from twisted.internet.threads import deferToThread

from mmc.site import mmcconfdir
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.core.tasks import TaskManager
from mmc.plugins.dashboard.manager import DashboardManager
from mmc.plugins.dashboard.panel import Panel

from mmc.plugins.msc.package_api import PackageGetA
from mmc.plugins.pulse2.utils import notificationManager
from mmc.plugins.pkgs.package_put_api import PackagePutA
from mmc.plugins.pkgs.user_packageapi_api import UserPackageApiApi
from mmc.plugins.pkgs.config import PkgsConfig
from pulse2.managers.location import ComputerLocationManager
import uuid
import json
from pulse2.version import getVersion, getRevision # pyflakes.ignore

from pulse2.database.pkgs import PkgsDatabase
from pulse2.database.xmppmaster import XmppMasterDatabase
import traceback
from mmc.plugins.xmppmaster.master.lib.utils import simplecommand, name_random
from unidecode import unidecode
import uuid
from xml.dom import minidom

logger = logging.getLogger()

APIVERSION = "0:0:0"

def getApiVersion(): return APIVERSION


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class pkgmanage():

    def __init__(self, args=(), kwargs=None):
        self.args = args
        self.kwargs = kwargs

    def list_all(self, param):
        return PkgsDatabase().list_all()

    def add_package(self, package):
        return PkgsDatabase().createPackage(package)

    def pkgs_register_synchro_package(self, uuidpackage, typesynchro):
        return PkgsDatabase().pkgs_register_synchro_package(uuidpackage, typesynchro)

    def pkgs_delete_synchro_package(self, uuidpackage):
        return PkgsDatabase().pkgs_delete_synchro_package(uuidpackage)

    def get_relayservers_no_sync_for_packageuuid(self, uuidpackage):
        return PkgsDatabase().get_relayservers_no_sync_for_packageuuid(uuidpackage)

    def remove_package(self, uuid):
        return PkgsDatabase().remove_package(uuid)

    def refresh_dependencies(self, uuid, dependencies_list):
        PkgsDatabase().refresh_dependencies(uuid, dependencies_list)

def dirpackage():
    return PkgsDatabase().dirpackage

def list_all():
    return pkgmanage().list_all()

############### synchro syncthing package #####################
def pkgs_register_synchro_package(uuidpackage, typesynchro):
    return pkgmanage().pkgs_register_synchro_package(uuidpackage, typesynchro)

def pkgs_delete_synchro_package(uuidpackage):
    return pkgmanage().pkgs_delete_synchro_package(uuidpackage)

def pkgs_get_info_synchro_packageid(uuidpackage):
    list_relayservernosync = pkgmanage().get_relayservers_no_sync_for_packageuuid(uuidpackage)
    list_relayserver = XmppMasterDatabase().getRelayServer(enable = True )
    return [list_relayservernosync, list_relayserver]

def associatePackages(pid, fs, level = 0):
    tmp_input_dir = os.path.join("/","var","lib", "pulse2", "package-server-tmpdir")
    packages_input_dir = os.path.join("/", "var", "lib", "pulse2", "packages")
    destination = os.path.join(packages_input_dir, pid )
    errortransfert = []
    result = []
    boolsucess = True
    if len(fs) > 0:
        # file a associe
        for repfiles in fs:
            source = os.path.join(tmp_input_dir, repfiles )
            cmd = "rsync -a %s/ %s/"%( source, destination )
            rest = simplecommand(cmd)
            if rest['code'] != 0:
                boolsucess = False
                errortransfert.append(rest['code'])
            #efface repertoire
            simplecommand("rm -rf %s"%source)
    return [ boolsucess, errortransfert ]

def _remove_non_ascii(text):
    return unidecode(unicode(text, encoding = "utf-8"))

def _create_uuid_sympa(label):
    data = _remove_non_ascii((str(uuid.uuid1())[:9] + label+"_").replace(' ', '_'))
    data = name_random(36 , pref=data)[:36]
    return data

def to_json_xmppdeploy( package):
        """
            create JSON xmppdeploy descriptor
        """
        execscript = 0
        if package['reboot']:
            success = execscript + 2
        else:
            success = execscript + 1
        error = success + 1
        ###------------------------
        ### metaparameter
        ###------------------------
        metaparameter = { "os": [ package['targetos'] ] }
        metaparameter[package['targetos']] = {
                                                "label": {
                                                            "END_ERROR"      : error,
                                                            "END_SUCCESS"    : success,
                                                            "EXECUTE_SCRIPT" : execscript
                                                }
        }
        sequence = []
        ###------------------------
        ### actionprocessscriptfile
        ###------------------------
        sequence .append({ "step": 0,
                           "action": "actionprocessscriptfile",
                           "@resultcommand": "@resultcommand",
                           "actionlabel": "EXECUTE_SCRIPT",
                           "codereturn": "",
                           "error": error,
                           "script": package['command']['command'],
                           "success": success,
                           "typescript": "Batch" })
        ###------------------------
        ### actionrestart
        ###------------------------
        if package['reboot']:
            sequence .append({ "action": "actionrestart",
                               "actionlabel": "REBOOT",
                               "step": 1})
        ###------------------------
        ### actionsuccescompletedend
        ###------------------------
        dsuccess = { "action": "actionsuccescompletedend",
                     "actionlabel": "END_SUCCESS",
                     "clear": "True",
                     "inventory" : "True",
                     "step": success}
        #if str(package['associateinventory']) != "0":
            #dsuccess['inventory'] = "True"
        #else:
            #dsuccess['inventory'] = "False"
        sequence .append(dsuccess)
        ###------------------------
        ### actionerrorcompletedend
        ###------------------------
        sequence .append({"step": error,
                          "action": "actionerrorcompletedend",
                          "actionlabel": "END_ERROR"})
        ###------------------------
        ### info
        ###------------------------
        data = {
            "info": { "Dependency": [],
                      "description": package['description'],
                      "metagenerator": "standard",
                      "methodetransfert": "pullcurl",
                      "name": str(package['label'] + ' ' +
                                  package['version'] + ' (' +
                                  package['id']+')'),
                      "software": package['label'],
                      "transferfile": True,
                      "version": package['version']
            }
        }

        data['metaparameter'] = metaparameter
        data[package['targetos']]={}
        data[package['targetos']]['sequence'] = sequence

        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

def putPackageDetail( package, need_assign = True):
    if package['id'] == "" :
        # create uuid
        #package['id'] = str( uuid.uuid1())
        package['id'] = _create_uuid_sympa(package['label'])
    if len(package['id']) != 36:
        return False
    packages_input_dir = os.path.join("/", "var", "lib", "pulse2", "packages")
    packages_id_input_dir = os.path.join("/", "var", "lib", "pulse2", "packages", package['id'] )

    if packages_input_dir == packages_id_input_dir:
        return False
    # si le dossier n existe pas alors le creéer
    if not os.path.isdir(packages_id_input_dir):
        os.mkdir(packages_id_input_dir, 0755)
    confjson={
        "sub_packages" : [],
        "description" : package['description'],
        "entity_id" : "0",
        "id" : package['id'],
        "commands" :{
            "postCommandSuccess" : {"command" : "", "name" : ""},
            "installInit" : {"command" : "", "name" : ""},
            "postCommandFailure" : {"command" : "", "name" : ""},
            "command" : {
                "command" : package['command']['command'],
                "name" : ""},
            "preCommand": {"command" : "", "name" : ""}
        },
        "name" : package['label'],
        "targetos" : package['targetos'],
        "reboot" : package['reboot'],
        "version" : package['version'],
        "metagenerator" : package['metagenerator'],
        "inventory" : {
            "associateinventory" : str(package['associateinventory']),
            "licenses": package['licenses'],
            "queries": {
                "Qversion": package['Qversion'],
                "Qvendor": package['Qvendor'],
                "boolcnd": package['boolcnd'],
                "Qsoftware": package['Qsoftware']
            }
        }
    }
    # writte file to xmpp deploy
    xmppdeployfile = to_json_xmppdeploy(package)
    fichier = open( os.path.join(packages_id_input_dir,"xmppdeploy.json"), "w" )
    fichier.write(xmppdeployfile)
    fichier.close()
    # Add the package into the database
    pkgmanage().add_package(confjson)

    # write file to package directory
    with open( os.path.join(packages_id_input_dir,"conf.json"), "w" ) as outfile:
        json.dump(confjson, outfile, indent = 4)

    result = package
    package['postCommandSuccess'] = {"command" : "", "name" : ""}
    package['installInit'] = {"command" : "", "name" : ""},
    package['postCommandFailure'] = {"command" : "", "name" : ""}
    package['preCommand'] =  {"command" : "", "name" : ""}
    result = [True, package['id'], packages_id_input_dir, package]
    return result

def pkgs_getTemporaryFiles():
    logging.getLogger().debug("getTemporaryFiles")
    ret = []
    tmp_input_dir = os.path.join("/", "var", "lib", "pulse2", "package-server-tmpdir")
    if os.path.exists(tmp_input_dir):
        for f in os.listdir(tmp_input_dir):
            ret.append([f, os.path.isdir(os.path.join(tmp_input_dir, f))])
    return ret

def getTemporaryFileSuggestedCommand1(tempdir):
    tmp_input_dir = os.path.join("/","var","lib", "pulse2", "package-server-tmpdir")
    ret = {
            "version": '0.1',
            "commandcmd": [],
        }
    suggestedCommand = []
    if not isinstance(tempdir, list):
        if os.path.exists(tmp_input_dir):
            for f in os.listdir(os.path.join(tmp_input_dir, tempdir)):
                fileadd = os.path.join(tmp_input_dir, tempdir, f)
                if os.path.isfile(fileadd):
                    c = getCommand(fileadd)
                    command = c.getCommand()
                    if command is not None:
                        suggestedCommand.append(command)
                    else:
                        # No proposition found : try with the new parser
                        rules = PkgsDatabase().list_all_extensions()
                        filename = fileadd.split("/")[-1]
                        filebasename = filename.split(".")[0]
                        fileextension = filename.split(".")[-1]

                        for rule in rules:
                            proposition = ''
                            test_proposition = True
                            proposition = rule['proposition']

                            if 'name' in rule and rule['name'] != "":
                                if not re.search(rule['name'], filebasename, re.IGNORECASE):
                                    test_proposition = False
                            if 'extension' in rule and rule['extension'] != "":
                                if not re.search(rule['extension'], fileextension, re.IGNORECASE):
                                    test_proposition = False
                            if 'magic_command' in rule and rule['magic_command'] != "":
                                pass

                            if 'bang' in rule and rule['bang'] != "":
                                pass

                            if 'file' in rule and rule['file'] != "":
                                result = simplecommand("file %s"%fileadd.replace(" ", "\ "))
                                if result['code'] == 0:
                                    result = result['result'][0]
                                    if re.search(rule['file'], result, re.IGNORECASE) is None:
                                        test_proposition = False
                                else:
                                    test_proposition = False

                            if 'string_head' in rule and rule['string_head'] != "":
                                pass

                            if 'string_tail' in rule and rule['string_tail'] != "":
                                pass

                            # If all the criterion's rule are validate, no need to test an another rule
                            # This one is corresponding with the
                            if test_proposition is True:
                                logging.getLogger().warning(proposition, filename)
                                ret['commandcmd'] = proposition% filename
                                return ret

    ret['commandcmd'] = '\n'.join(suggestedCommand)
    return ret


def pushPackage(random_dir, files, local_files):
    tmp_input_dir = os.path.join("/","var","lib", "pulse2", "package-server-tmpdir")
    logging.getLogger().info("pushing package from a local mmc-agent")
    if not os.path.exists(tmp_input_dir):
        os.makedirs(tmp_input_dir)
    filepath = os.path.join(tmp_input_dir, random_dir)
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    for file in files:
        logging.getLogger().debug("Move file : %s to %s "%( os.path.join(file['tmp_dir'],
                                                            random_dir, file['filename']),os.path.join(filepath, file['filename'])))
        try:
            shutil.move(os.path.join(file['tmp_dir'], random_dir, file['filename']), \
                            os.path.join(filepath, file['filename']))
            os.chmod(os.path.join(filepath, file['filename']), 0660)
        except (shutil.Error, OSError, IOError):
            logging.getLogger().error("%s"%(traceback.format_exc()))
            return False
    return True

def removeFilesFromPackage( pid, files):
    tmp_input_dir = os.path.join("/", "var", "lib", "pulse2", "packages")
    ret = []
    success=[]
    error=[]
    if pid != '' and len(files) > 0:
        for filedelete in files:
            filepath = os.path.join(tmp_input_dir, pid, filedelete)
            if os.path.isfile(filepath):
                try:
                    os.remove(filepath)
                    success.append(filedelete)
                except OSError as e:
                    error.append("%s : %s"%(filedelete, str(e)))
    else:
        error.append("error file missing for deleted : %s"%(files))
    ret.append(success)
    ret.append(error)
    return ret

def list_all_extensions():
    return pkgmanage().list_all_extensions()

def activate():
    logger = logging.getLogger()
    logger.debug("Pkgs is activating")
    config = PkgsConfig("pkgs")
    if config.disabled:
        logger.warning("Plugin pkgs: disabled by configuration.")
        return False

    DashboardManager().register_panel(Panel('appstream'))

    #TaskManager().addTask("pkgs.updateAppstreamPackages",
    #                    (updateAppstreamPackages,),
    #                    cron_expression='23 10 * * *')
    if not PkgsDatabase().activate(config):
        logger.warning("Plugin Pkgs: an error occurred during the database initialization")
        return False
    return True

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s

class ConfigReader(object):
    """Read and parse config files"""
    def __init__(self):
        agent_ini = os.path.join(mmcconfdir,
                                "agent",
                                "config.ini")
        self._agent_config = self.get_config(agent_ini)


    @classmethod
    def get_config(cls, inifile):
        """
        Get the configuration from config file

        Args:
        inifile: path to config file

        Returns:
        ConfigParser.ConfigParser instance
        """
        logging.getLogger().debug("Load config file %s" % inifile)
        if not os.path.exists(inifile) :
            logging.getLogger().error("Error while reading the config file: Not found.")
            return False

        config = ConfigParser()
        config.readfp(open(inifile))
        if os.path.isfile(inifile + '.local'):
            config.readfp(open(inifile + '.local', 'r'))

        return config

    @property
    def agent_config(self):
        """
        Get the configuration of package server

        @return: ConfigParser.ConfigParser instance
        """
        return self._agent_config

class RpcProxy(RpcProxyI):
    def getPApiDetail(self, pp_api_id):
        def _getPApiDetail(result, pp_api_id = pp_api_id):
            for upa in result:
                if upa['uuid'] == pp_api_id:
                    return upa
            return False

        d = self.upaa_getUserPackageApi()
        d.addCallback(_getPApiDetail)
        return d

    # PackagePutA
    #def ppa_getPackageDetail(self, pp_api_id, pid):
        #def _ppa_getPackageDetail(result, pp_api_id = pp_api_id, pid = pid):
            #for upa in result:
                #if upa['uuid'] == pp_api_id:
                    #return PackageGetA(upa).getPackageDetail(pid)
            #return False
        #d = self.upaa_getUserPackageApi()
        #d.addCallback(_ppa_getPackageDetail)
        #return d

    #def ppa_pushPackage(self, pp_api_id, random_dir, files, local_mmc):
        #def _ppa_pushPackage(result, pp_api_id = pp_api_id, random_dir = random_dir, files = files, local_mmc = local_mmc):
            #def _encodeFiles(random_dir, files):
                #encoded_files = []
                #for file in files:
                    #logging.getLogger().debug("Encoding file %s" % file['filename'])
                    #tmp_dir = file['tmp_dir']
                    #f = open(os.path.join(tmp_dir, random_dir, file['filename']), 'r')
                    #encoded_files.append({
                        #'filename': file['filename'],
                        #'filebinary': b64encode(f.read()),
                    #})
                    #f.close()
                #return encoded_files

            #def _decodeFiles(random_dir, files):
                #pkgs_tmp_dir = self.getPServerTmpDir()
                #if not os.path.exists(os.path.join(pkgs_tmp_dir, random_dir)):
                    #os.makedirs(os.path.join(pkgs_tmp_dir, random_dir))
                #filepath = os.path.join(pkgs_tmp_dir, random_dir)
                #for file in files:
                    #logging.getLogger().debug("Decoding file %s" % file['filename'])
                    #f = open(os.path.join(filepath, file['filename']), 'w')
                    #f.write(b64decode(file['filebinary']))
                    #f.close()
                    #file['filebinary'] = False
                    #file['tmp_dir'] = pkgs_tmp_dir
                #return files

            #for upa in result:
                #if upa['uuid'] == pp_api_id:
                    #local_pserver = self.getPServerIP() in ['localhost', '127.0.0.1'] and True or False
                    #if local_mmc:
                        #logging.getLogger().info("Push package from local mmc-agent...")
                        #if local_pserver:
                            #logging.getLogger().info("... to local package server")
                            #return PackagePutA(upa).pushPackage(random_dir, files, local_pserver)
                        #else:
                            #logging.getLogger().info("... to external package server")
                            ## Encode files (base64) and send them with XMLRPC
                            #encoded_files = _encodeFiles(random_dir, files)
                            #return PackagePutA(upa).pushPackage(random_dir, encoded_files, local_pserver)
                    #else:
                        #logging.getLogger().info("Push package from external mmc-agent...")
                        #if local_pserver:
                            #logging.getLogger().info("... to local package server")
                            ## decode files
                            #decoded_files = _decodeFiles(random_dir, files)
                            #return PackagePutA(upa).pushPackage(random_dir, decoded_files, local_pserver)
                        #else:
                            #logging.getLogger().info("... to external package server")
                            #return PackagePutA(upa).pushPackage(random_dir, files, local_pserver)
            #logging.getLogger().warn("Failed to push package on %s"%(pp_api_id))
            #return False
        #d = self.upaa_getUserPackageApi()
        #d.addCallback(_ppa_pushPackage)
        #return d

    #def ppa_putPackageDetail(self, pp_api_id, package, need_assign = True):
        #print json.dumps(package, indent=4)
        ## Patching package with entity_id
        #ctx = self.currentContext
        #locations = ComputerLocationManager().getUserLocations(ctx.userid)
        ## Get root location for the user
        #root_location_id = locations[0]['uuid'].replace('UUID', '')
        #package['entity_id'] = root_location_id
        #logging.getLogger().fatal(locations)
        #def _ppa_putPackageDetail(result, pp_api_id = pp_api_id, package = package, need_assign = need_assign):
            #for upa in result:
                #if upa['uuid'] == pp_api_id:
                    #return PackagePutA(upa).putPackageDetail(package, need_assign)
            #logging.getLogger().warn("Failed to put package details on %s"%(pp_api_id))
            #return False
        #d = self.upaa_getUserPackageApi()
        #d.addCallback(_ppa_putPackageDetail)
        #return d

    #def ppa_dropPackage(self, pp_api_id, pid):
        #logging.getLogger().info('I will drop package %s/%s' % (pp_api_id, pid))
        #def _ppa_dropPackage(result, pp_api_id = pp_api_id, pid = pid):
            #for upa in result:
                #if upa['uuid'] == pp_api_id:
                    #return PackagePutA(upa).dropPackage(pid)
            #return False
        #d = self.upaa_getUserPackageApi()
        #d.addCallback(_ppa_dropPackage)
        #return d

    #def ppa_getTemporaryFiles(self, pp_api_id):
        #def _ppa_getTemporaryFiles(result, pp_api_id = pp_api_id):
            #for upa in result:
                #if upa['uuid'] == pp_api_id:
                    #return PackagePutA(upa).getTemporaryFiles()
            #return []
        #d = self.upaa_getUserPackageApi()
        #d.addCallback(_ppa_getTemporaryFiles)
        #return d

    #def ppa_getTemporaryFileSuggestedCommand(self, pp_api_id, tempdir):
        #def _ppa_getTemporaryFilesSuggestedCommand(result, pp_api_id = pp_api_id, tempdir = tempdir):
            #for upa in result:
                #if upa['uuid'] == pp_api_id:
                    #return PackagePutA(upa).getTemporaryFilesSuggestedCommand(tempdir)
            #return []
        #d = self.upaa_getUserPackageApi()
        #d.addCallback(_ppa_getTemporaryFilesSuggestedCommand)
        #return d

    #def ppa_associatePackages(self, pp_api_id, pid, files, level = 0):
        #def _ppa_associatePackages(result, pp_api_id = pp_api_id, pid = pid, files = files, level = level):
            #for upa in result:
                #if upa['uuid'] == pp_api_id:
                    #return PackagePutA(upa).associatePackages(pid, files, level)
            #return []
        #d = self.upaa_getUserPackageApi()
        #d.addCallback(_ppa_associatePackages)
        #return d


    #def ppa_removeFilesFromPackage(self, pp_api_id, pid, files):
        #def _ppa_removeFilesFromPackage(result, pp_api_id = pp_api_id, pid = pid, files = files):
            #for upa in result:
                #if upa['uuid'] == pp_api_id:
                    #return PackagePutA(upa).removeFilesFromPackage(pid, files)
            #return []
        #d = self.upaa_getUserPackageApi()
        #d.addCallback(_ppa_removeFilesFromPackage)
        #return d

    #def ppa_getRsyncStatus(self, pp_api_id, pid):
        #def _ppa_getRsyncStatus(result, pp_api_id = pp_api_id, pid = pid):
            #for upa in result:
                #if upa['uuid'] == pp_api_id:
                    #return PackagePutA(upa).getRsyncStatus(pid)
            #return []
        #d = self.upaa_getUserPackageApi()
        #d.addCallback(_ppa_getRsyncStatus)
        #return d

    # UserPackageApiApi
    def upaa_getUserPackageApi(self):
        # cf class UserPackageApi package_server/user_package_api/__init__.py
        ctx = self.currentContext
        return UserPackageApiApi().getUserPackageApi(ctx.userid)

    #def getMMCIP(self):
        #config = ConfigReader()

        #self.agent_config = config.agent_config

        #return self.agent_config.get("main", "host")

    #def getPServerIP(self):
        #config = PkgsConfig("pkgs")
        #return config.upaa_server

    #def getPServerTmpDir(self):
        #config = PkgsConfig("pkgs")
        #return config.tmp_dir


class DownloadAppstreamPackageList(object):
    """
    Create list of Appstream who need to be downloaded and download them
    """
    def __init__(self):
        """
        This method initialize the class.
        By default there is no working update
        """
        self.download_packages= {}
        self.update=False

    def _add_appstream(self,package_name):
        """
        This methods add package in the dict of
        package who need to be download and set it to "wait"
        status.

        Args:
        package_name: name of the package in the appstream

        """
        self.download_packages[package_name]="wait"

    def _start_appstream(self,package_name):
        """
        This methods set package in the dict of
        package who need to be download, to "downloading"
        status.
        """
        self.download_packages[package_name]="download"

    def _finish_appstream(self,package_name):
        """
        This methods delete a package in the dict of
        not yet downloaded appstream packages.
        """
        if package_name in self.download_packages:
            self.download_packages.pop(package_name)

    def getDownloadAppstreamPackages(self):
        """
        This methods return dict of packages who need
        to be download
        @rtype: dict of unicode like { 'package_name' : 'status' } ,
            valid status are "download" and "wait".
        @return: list of new appstream packages name who are not
        yet downloaded.
        """
        return self.download_packages

    def updateAppstreamPackages(self):
        """
        This methode update appstream package and download package who need to be
        download. It can effectly work only one at a time.
        @rtype: bool
        @return: True if done,False if already working.
        """
        # if an other update is working, don't update.
        if self.update:
            return False
        self.update=True

        tempfile.tempdir='/var/tmp/'
        logger = logging.getLogger()
        appstream_url = PkgsConfig("pkgs").appstream_url

        #add non downloaded package to download package list
        for pkg, details in getActivatedAppstreamPackages().iteritems():

            try:
                # Creating requests session
                s = requests.Session()
                s.auth = ('appstream', details['key'])
                base_url = '%s/%s/' % (appstream_url, pkg)

                # Get Package uuid
                r = s.get(base_url + 'info.json')
                if not r.ok:
                    raise Exception("Cannot get package metadata. Status: %d" % (r.status_code))
                info = parse_json(r.content.strip())
                uuid = info['uuid']

                # If package is already downloaded, skip
                logger.debug('Got UUID %s, checking if it already exists ...' % uuid)
                if not uuid or os.path.exists('/var/lib/pulse2/appstream_packages/%s/' % uuid):
                    continue
                #add package to download package list
                self._add_appstream(pkg)

            except Exception, e:
                logger.error('Appstream: Error while fetching package %s' % pkg)
                logger.error(str(e))

        #Download packages (copy dictionnary to be able to delete entry while iterate)
        for pkg,state in self.getDownloadAppstreamPackages().copy().iteritems():
            # download only wait package
            if state != "wait":
                continue
            logger.debug('Package %s will be download' % pkg)
            details=getActivatedAppstreamPackages()[pkg]
            try:
                # Creating requests session
                s = requests.Session()
                s.auth = ('appstream', details['key'])
                base_url = '%s/%s/' % (appstream_url, pkg)
                package_dir = None

                # Get Package uuid
                r = s.get(base_url + 'info.json')
                if not r.ok:
                    raise Exception("Cannot get package metadata. Status: %d" % (r.status_code))
                info = parse_json(r.content.strip())
                uuid = info['uuid']

                self._start_appstream(pkg)
                # Creating package directory
                logger.debug('New package version, creating %s directory' % uuid)
                package_dir = '/var/lib/pulse2/appstream_packages/%s/' % uuid
                os.mkdir(package_dir)

                # Downloading third party binaries
                if info['downloads']:
                    logger.debug('I will now download third party packages')
                for filename, url, md5sum in info['downloads']:
                    # Downloading file
                    # thanks to http://stackoverflow.com/questions/11768214/python-download-a-file-over-an-ftp-server
                    logger.debug('Downloading %s from %s' % (filename, url))
                    with closing(urllib2.urlopen(url)) as r:
                        with open(package_dir+filename, 'wb') as f:
                            shutil.copyfileobj(r, f)
                    # TODO: if md5 is not null, do an md5 checksum of downloaded file

                # Download data file
                data_temp_file = tempfile.mkstemp()[1]
                logger.debug('Downloading package data file')

                with open(data_temp_file, 'wb') as handle:
                    # Important: For newer versions of python-requests, use stream=True instead of prefetch
                    r = s.get(base_url + 'data.tar.gz', prefetch=False)

                    if not r.ok:
                        raise Exception("Cannot download package data. Status: %d" % r.status_code)

                    for block in r.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)

                logger.debug('Extracting package data file')
                # Extracting data archive

                if subprocess.call('tar xvf %s -C %s' % (data_temp_file, package_dir), shell=True) != 0:
                    raise Exception('Cannot decompress data file')

                # Removing tempfile
                #os.remove(data_temp_file)

                n_title = details['label'] + ' has been updated to version ' + info['version']
                notificationManager().add('pkgs', n_title, '')
                self._finish_appstream(pkg);
            except Exception, e:
                logger.error('Appstream: Error while fetching package to be downloaded %s' % pkg)
                logger.error(str(e))
               # Removing package dir (if exists)
                try:
                    shutil.rmtree(package_dir)
                except Exception, e:
                    logger.error(str(e))

        self.update = False
        return True

dapl = DownloadAppstreamPackageList()

def get_installation_uuid():
    return open('/etc/pulse-licensing/installation_id').read().strip()

def lserv_query(cmd, options):
    settings = getAppstreamJSON()
    try:
        my_username = settings['my_username']
        my_password = settings['my_password']
    except KeyError:
        return -1

    url = 'https://activation.mandriva.com/' + cmd
    headers = {'content-type': 'application/json'}
    r = requests.get(\
                     url,
                     data=json.dumps(options),
                     headers=headers,
                     auth=(my_username, my_password)
                     )
    return json.loads(r.content)

def getAppstreamJSON():
    try:
        return json.loads(open('/etc/mmc/plugins/appstream.json').read())
    except:
        return {}

def setAppstreamJSON(data):
    try:
        f = open("/etc/mmc/plugins/appstream.json", "w")
        f.write(json.dumps(data))
        f.close()
        return True
    except Exception, e:
        logging.getLogger().error('Cannot write appstream JSON')
        logging.getLogger().error(str(e))
        return False


def getActivatedAppstreamPackages():
    json = getAppstreamJSON()
    if 'flows' in json:
        return json['flows']
    else:
        return {}

def getAvailableAppstreamPackages():
    return lserv_query('auth/customer/', {
        'name_licence' : 'appstream',
        'gui_product' : '-'
    })

def activateAppstreamFlow(id, package_name, package_label, duration):
    result = lserv_query('activate/licencing/', {
        'name_licence' : 'appstream',
        'gui_product' : get_installation_uuid(),
        'id' : id,
        'keypublique' : '=',
        'keysshpublique' : '='
    })
    key = result['licence'].strip()

    # Add key to appStream JSON
    json = getAppstreamJSON()
    if not 'flows' in json:
        json['flows'] = {}

    json['flows'][package_name] = {
        'id':id,
        'key':key,
        'label':package_label,
        'expiration_ts':int(time()) + int(duration) * 30.5 * 24 * 3600
    }
    setAppstreamJSON(json)
    updateAppstreamPackages()
    return True


def getDownloadAppstreamPackages():
    """
    This methods give new appstream packages who are not
    yet downloaded.

    Returns:
    list of new appstream packages name who are not
    yet downloaded.
    """
    return dapl.getDownloadAppstreamPackages()

def updateAppstreamPackages():
    """
    This methode create a thread to update appstream packages.
    """
    d = deferToThread(dapl.updateAppstreamPackages)
    d.addCallback(_cb_updateAppstreamPackages)
    d.addErrback(_eb_updateAppstreamPackages)
    return True

def _cb_updateAppstreamPackages(reason):
    """
    This methode is the callback of updateAppstreamPackages
    """
    logger = logging.getLogger()
    logger.info("Update of appstream packages finished correctly ")
    return reason

def _eb_updateAppstreamPackages(failure):
    """
    This method is the error Back of updateAppstreamPackages
    """
    logger = logging.getLogger()
    logger.warning("Update of appstream packages failed : %s " % repr(failure))

def getAppstreamNotifications():
    return notificationManager().getModuleNotification('pkgs')


def _path_package():
    return os.path.join("/", "var", "lib", "pulse2", "packages")

def save_xmpp_json(folder, json_content):
    structpackage = json.loads(json_content)
    keysupp = [ "actionlabel",
                "p_api",
                "id",
                "random_dir",
                "Qversion",
                "codereturn",
                "Qsoftware",
                "Qvendor",
                "files_uploaded",
                "step",
                "command",
                "action",
                "success",
                "error",
                "timeout",
                "boolcnd",
                "targetos",
                "resultcommand",
                "metaparameter",
                "clear"
                ]
    for z in structpackage['info']:
        if z.startswith('old_') or z.endswith('lastlines') or z.endswith('firstlines'):
            keysupp.append(z)
    for y in keysupp:
        try:
            del structpackage['info'][y]
        except :
            pass

    if not 'Dependency' in structpackage['info']:
        structpackage['info']['Dependency'] = []
    if not 'software' in structpackage['info']:
        structpackage['info']['software'] = structpackage['info']['name']

    structpackage['metaparameter'] = {}
    listos =[]

    if 'linux' in structpackage:
        listos.append('linux')
        structpackage['metaparameter']['linux']={}
    if "darwin" in structpackage:
        listos.append('darwin')
        structpackage['metaparameter']['darwin']={}
    if "win" in structpackage:
        listos.append('win')
        structpackage['metaparameter']['win']={}

    structpackage['metaparameter']['os'] = listos

    for osmachine in listos:
        vv = structpackage['metaparameter'][osmachine]
        vv['label']={}
        for stepseq in structpackage[osmachine]['sequence']:
            vv['label'][stepseq['actionlabel']] = stepseq['step']

    for osmachine in listos:
        vv = structpackage['metaparameter'][osmachine]['label']
        for stepseq in structpackage[osmachine]['sequence']:
            if "success" in stepseq:
                valsuccess = _stepforalias(stepseq['success'], vv)
                if valsuccess != None:
                    stepseq['success'] = valsuccess
            if "error" in stepseq:
                valerror = _stepforalias(stepseq['error'], vv)
                if valerror != None:
                    stepseq['error'] = valerror
    json_content= json.dumps(structpackage)
    _save_xmpp_json(folder, json_content)
    # Refresh the dependencies list
    uuid = folder.split('/')[-1]
    dependencies_list = structpackage['info']['Dependency']
    pkgmanage().refresh_dependencies(uuid, dependencies_list)

def _aliasforstep(step, dictstepseq):
    for t in dictstepseq:
        if dictstepseq[t] == step:
            return t
    return None

def _stepforalias(alias, dictstepseq):
    print "alias",alias
    for t in dictstepseq:
        print t
        if t == alias:
            return dictstepseq[t]
    return None

def _save_xmpp_json(folder, json_content):
    """
    Save the xmpp json package into new package

    Args:
    folder: Folder where the json file is stored
    json_content: Content of the json file

    Returns:
    bool:
    """

    try:
        content = json.loads(json_content)
    except ValueError:
        return False

    if not os.path.exists(folder):
        os.mkdir(folder, 0755)

    xmppdeploy = open(os.path.join(folder,'xmppdeploy.json' ),'w')
    json.dump(content,xmppdeploy,indent=4)

    xmppdeploy.close()
    return True

def xmpp_packages_list():
    """
    Create a list of xmpp packages and return the list and the information for each of them
    Returns:
    list of packages
    """

    path = _path_package()

    # 1 - list the packages directories
    list_all = os.listdir(path)
    xmpp_list = []

    for dirname in list_all:
        # 2 - if the directory contains xmppdeploy.json
        if os.path.isfile(os.path.join(path, dirname, 'xmppdeploy.json')) is True:
            # 3 - Extracts the package information and add it to the package list
            #json_content = json.load(file(path+'/'+dirname+'/xmppdeploy.json'))
            json_content = json.load(file(os.path.join(path, dirname, 'xmppdeploy.json')))
            json_content['info']['uuid'] = dirname;
            xmpp_list.append(json_content['info'])
    return xmpp_list

def remove_xmpp_package(package_uuid):
    """
    Remove the specified xmpp package. If it is ok, return true, else return false

    Args:
    package_uuid: uuid of the package

    Returns:
    success | failure
    """

    # If the package exists, delete it and return true
    pathpackagename = os.path.join(_path_package(), package_uuid)
    if os.path.exists(pathpackagename):
        shutil.rmtree(pathpackagename)
        # Delete the package from the bdd
        pkgmanage().remove_package(package_uuid)
        return True
    else :
        return False



def get_xmpp_package(package_uuid):
    """
    Select the specified package and return the information in the json
    :param package_uuid:  uuid of the package
    :return: the json or false if it does not exist
    """

    path = _path_package()

    if os.path.exists(os.path.join(path, package_uuid)):
        # Read all the content of the package
        json_file = open(os.path.join(path, package_uuid, 'xmppdeploy.json'), 'r')
        jsonstr = json_file.read()
        json_file.close()
        structpackage = json.loads(jsonstr)

        try:
            for os_seq in structpackage['metaparameter']['os']:
                vv = structpackage['metaparameter'][os_seq]['label']
                for stepseq in structpackage[os_seq]['sequence']:
                    if "success" in stepseq:
                        valalias = _aliasforstep(stepseq['success'], vv)
                        print valalias
                        if valalias != None:
                            stepseq['success'] = valalias
                    if "error" in stepseq:
                        valalias = _aliasforstep(stepseq['error'], vv)
                        if valalias != None:
                            stepseq['error'] = valalias
            try:
                del structpackage['metaparameter']
            except:
                pass
        except:
            pass
        jsonstr = json.dumps(structpackage)
        return jsonstr
    else:
        return False


def get_meta_from_xmpp_package(package_uuid):
    """
    Select the specified package and return the metaparameters in the json
    :param package_uuid: uuid of the package
    :return: return the json or false if it does not exists
    """

    path = _path_package()

    if os.path.exists(os.path.join(path, package_uuid)):
        # Read all the content of the package
        json_file = open(os.path.join(path, package_uuid, 'xmppdeploy.json'), 'r')
        jsonstr = json_file.read()
        json_file.close()
        structpackage = json.loads(jsonstr)

        try:
            #jsonstr(structpackage['metaparameter'])
            return structpackage['metaparameter']
        except:
            return False
    else:
        return False


def package_exists(uuid):
    """Test if the specified package exists
    Param:
        uuid str corresponds to the package uuid we are looking for
    Returns:
        boolean true if the package exists else false"""

    path = _path_package()

    if os.path.exists(os.path.join(path, uuid)):
        return True
    else:
        return False

class getCommand(object):
    def __init__(self, file):
        self.file = file
        self.logger =logging.getLogger()

    def getStringsData(self):
        """
        Get strings command output as XML string if <?xml is found
        else return all strings datas
        """
        strings_command = 'strings "%s"' % self.file
        filestrings_data = os.popen(strings_command)
        strings_data = filestrings_data.read()
        filestrings_data.close()

        xml_pos = strings_data.find('<?xml')
        if xml_pos != -1:
            strings_data = strings_data[xml_pos:]
            end_pos = strings_data.find('</assembly>') + 11
            return strings_data[:end_pos]
        else:
            self.logger.debug('getStringsData: <?xml tag not found :-(, return all strings_data')
            return strings_data

    def getFileData(self):
        """
        return file command output as dictionary
        """
        file_command = 'file "%s"' % self.file
        file_data = os.popen(file_command).read()
        l = file_data.split(': ')
        n = len(l)
        d = {}

        # this awful piece of code convert file output to a dictionnary
        for i in range(n-1, 0, -1):
            lcount = len(l[i].split(', '))
            if lcount == 1: lcount = 2 # lcount is at least equal to 2 to prevent empty values
            d[l[i-1].split(', ').pop()] = " ".join(l[i].split(', ')[:lcount-1]).replace('\n', '')

        return d

    def getAdobeCommand(self):
        return '"%s" /sAll' % basename(self.file)

    def getInnoCommand(self):
        return '"%s" /SP /VERYSILENT /NORESTART' % basename(self.file)

    def getNSISCommand(self):
        return '"%s" /S' % basename(self.file)

    def getNSISUpdateCommand(self):
        return '"%s" /S /UPDATE' % basename(self.file)

    def getMozillaCommand(self):
        return '"%s" -ms' % basename(self.file)

    def get7ZipCommand(self):
        return '"%s" /S' % basename(self.file)

    def getMSICommand(self):
        return """msiexec /qn /i "%s" ALLUSERS=1 CREATEDESKTOPLINK=0 ISCHECKFORPRODUCTUPDATES=0 /L install.log

if errorlevel 1 (
  type install.log
  echo "MSI INSTALLER FAILED WITH CODE %%errorlevel%%. SEE LOG ABOVE."
  exit /b %%errorlevel%%
) else (
  del /F install.log
  exit 0
)""" % basename(self.file)

    def getMSIUpdateCommand(self):
        """
        Command for *.msp files (MSI update packages)
        """
        return 'msiexec /p "%s" /qb REINSTALLMODE="ecmus" REINSTALL="ALL"' % basename(self.file)

    def getRegCommand(self):
        return 'regedit /s "%s"' % basename(self.file)

    def getDpkgCommand(self):
        return """export DEBIAN_FRONTEND=noninteractive
export UCF_FORCE_CONFFOLD=yes
dpkg -i --force-confdef --force-confold "%s" """ % basename(self.file)

    def getRpmCommand(self):
        return """if [ ! -e /etc/os-release ]; then
  echo "We are not able to find your linux distibution"
  exit 1
else
  . /etc/os-release
fi

case "$ID" in
  mageia)
    urpmi --auto "%s"
    ;;
  redhat|fedora)
    dnf -y install "%s"
    ;;
  *)
    echo "Your distribution is not supported yet or is not rpm based"
    exit 1
    ;;
esac""" %(basename(self.file), basename(self.file))

    def getAptCommand(self):
        return 'apt -q -y install "%s" --reinstall' % basename(self.file)

    def getBatCommand(self):
        return 'cmd.exe /c "%s"' % basename(self.file)

    def getShCommand(self):
        return './"%s"' % basename(self.file)

    def getCommand(self):
        self.logger.debug("Parsing %s:" % self.file)

        strings_data = self.getStringsData()
        file_data = self.getFileData()
        self.logger.debug("File data: %s" % file_data)

        if "PE32 executable" in file_data[self.file]:
            # Not an MSI file, maybe InnoSetup or NSIS
            self.logger.debug("%s is a PE32 executable" % self.file)
            installer = None

            # If strings_data startswith <?xml, it is propably
            # standard InnoSetup or NSIS installer
            # else, we check for another custom installer
            # (Adobe, ....)

            if strings_data.startswith('<?xml'):
                xmldoc = minidom.parseString(strings_data)
                identity = xmldoc.getElementsByTagName('assemblyidentity')

                if len(identity) == 0:
                    # if assemblyIdentity don't exists, try assemblyIdentity
                    identity = xmldoc.getElementsByTagName('assemblyIdentity')

                if identity > 0:
                    if identity[0].hasAttribute('name'):
                        installer = identity[0].getAttribute('name')
                        self.logger.debug("Installer: %s" % installer)
            elif 'AdobeSelfExtractorApp' in strings_data:
                self.logger.debug('Adobe application detected')
                return self.getAdobeCommand()

            if installer == "JR.Inno.Setup":
                self.logger.debug("InnoSetup detected")
                return self.getInnoCommand()
            elif installer == "Nullsoft.NSIS.exehead":
                self.logger.debug("NSIS detected")
                if re.match('^pulse2-secure-agent-.*\.exe$', basename(self.file)) and not re.search('plugin', basename(self.file)):
                    self.logger.debug("Pulse Secure Agent detected, add /UPDATE flag")
                    return self.getNSISUpdateCommand()
                return self.getNSISCommand()
            elif installer == "7zS.sfx.exe":
                self.logger.debug("7zS.sfx detected (Mozilla app inside ?)")
                if not os.system("grep Mozilla '%s' > /dev/null" % self.file): # return code is 0 if file match
                    self.logger.debug("Mozilla App detected")
                    return self.getMozillaCommand()
                else:
                    return self.logger.info("I can't get a command for %s" % self.file)
            elif installer == "7-Zip.7-Zip.7zipInstall":
                self.logger.debug("7-Zip detected")
                return self.get7ZipCommand()
            else:
                return self.logger.info("I can't get a command for %s" % self.file)

        elif "Name of Creating Application" in file_data:
            # MSI files are created with Windows Installer, but some apps like Flash Plugin, No
            if "Windows Installer" in file_data['Name of Creating Application'] or "Document Little Endian" in file_data[self.file]:
                # MSI files
                if re.match('(x64|Intel);[0-9]+', file_data['Template']):
                    if self.file.endswith('.msp'):
                        self.logger.debug("%s is a MSI Update file" % self.file)
                        return self.getMSIUpdateCommand()
                    else:
                        self.logger.debug("%s is a MSI file" % self.file)
                        return self.getMSICommand()
                else:
                    return self.logger.info("No Template Key for %s" % self.file)
        elif "Debian binary package" in file_data[self.file] or self.file.endswith(".deb"):
            self.logger.debug("Debian package detected")
            return self.getDpkgCommand()
        elif self.file.endswith(".reg"):
            self.logger.debug("Reg file detected")
            return self.getRegCommand()
        elif self.file.endswith(".bat"):
            self.logger.debug("MS-DOS Batch file detected")
            return self.getBatCommand()
        elif self.file.endswith(".sh"):
            self.logger.debug("sh file detected")
            return self.getShCommand()
        elif self.file.endswith(".rpm"):
            self.logger.debug("rpm file detected")
            return self.getRpmCommand()
        else:
            return self.logger.info("I don't know what to do with %s (%s)" % (self.file, file_data[self.file]))
