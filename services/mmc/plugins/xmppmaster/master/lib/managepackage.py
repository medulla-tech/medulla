#!/usr/bin/env python
# -*- coding: utf-8; -*-
# 
# (c) 2016-2021 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import uuid
import re
import sys, os
import os.path
import json
import logging
from utils import md5, simplecommand
from pulse2.database.xmppmaster import XmppMasterDatabase
from pulse2.database.pkgs import PkgsDatabase
logger = logging.getLogger()

class apimanagepackagemsc:
    exclude_name_package = ["sharing", ".stfolder", ".stignore" ]

    @staticmethod
    def readjsonfile(namefile):
        with open(namefile) as json_data:
            data_dict = json.load(json_data)
        return data_dict

    @staticmethod
    def search_list_package():
        """
            This function searches packages in the global and
            local shares.
        """
        packagelist = []
        dirpackage = os.path.join("/", "var", "lib", "pulse2", "packages")
        global_package_folder = os.path.join(dirpackage, "sharing", "global")
        packagelist = [os.path.join(global_package_folder, f)
                for f in os.listdir(global_package_folder) if len(f) == 36]
        local_package_folder  = os.path.join(dirpackage, "sharing")
        share_pathname = [os.path.join(local_package_folder, f)
                for f in os.listdir(local_package_folder) if f != "global"]
        for part in share_pathname:
            filelist = [os.path.join(part, f) for f in os.listdir(part) if len(f) == 36]
            packagelist += filelist
        return packagelist

    @staticmethod
    def package_for_deploy_from_share():
        """
            This function creates symlinks in the packages directory
            to the target in the local/global share
        """
        dirpackage = os.path.join("/", "var", "lib", "pulse2", "packages")
        for package in search_list_package():
            os.symlink(package , os.path.join(dirpackage, os.path.basename(package)))

    @staticmethod
    def remove_symlinks():
        """
        This function remove symlinks
        """
        dirpackage = os.path.join("/", "var", "lib", "pulse2", "packages")
        packagelist = [os.path.join(dirpackage, package) for package in os.listdir(dirpackage) if len(package) == 36]
        for package in packagelist:
            if os.path.islink(package) and not os.path.exists(package):
                os.remove(package)

    @staticmethod
    def packagelistmsc():
        folderpackages = os.path.join("/", "var" ,"lib","pulse2","packages")
        return [ os.path.join(folderpackages,x) for x in os.listdir(folderpackages) \
            if os.path.isdir(os.path.join(folderpackages,x)) \
                and x not in apimanagepackagemsc.exclude_name_package]

    @staticmethod
    def listfilepackage(folderpackages):
        return [ os.path.join(folderpackages,x) for x in os.listdir(folderpackages) \
            if not os.path.isdir(os.path.join(folderpackages,x)) \
                and x not in apimanagepackagemsc.exclude_name_package]

    @staticmethod
    def packagelistmscconfjson(pending = False):
        folderpackages = os.path.join("/", "var" ,"lib","pulse2","packages")
        listfichierconf =  [ os.path.join(folderpackages,x,"conf.json") \
            for x in os.listdir(folderpackages) \
                if os.path.isdir(os.path.join(folderpackages,x)) \
                    and x not in apimanagepackagemsc.exclude_name_package]
        listpackagependig = PkgsDatabase().list_pending_synchro_package()
        listpendingfichierconf = []
        listnotpendingfichierconf = []
        for pathuuidpackage in listfichierconf:
            nameuuid = os.path.basename(os.path.dirname(pathuuidpackage))
            if nameuuid in listpackagependig:
                listpendingfichierconf.append(pathuuidpackage)
            else:
                listnotpendingfichierconf.append(pathuuidpackage)
        if pending:
            return listpendingfichierconf
        else:
            return listnotpendingfichierconf

    @staticmethod
    def sizedirectory(path):
        size = 0
        for root, dirs, files in os.walk(path):
            for fic in files:
                size += os.path.getsize(os.path.join(root, fic))
        return size

    @staticmethod
    def getPackageDetail(pid):
        result={}
        package = os.path.join("/", "var" , "lib", "pulse2", "packages", pid, "conf.json")
        datapacquage = apimanagepackagemsc.readjsonfile(package)
        result['postCommandSuccess'] = datapacquage['commands']['postCommandSuccess']
        result['preCommand'] = datapacquage['commands']['preCommand']
        result['installInit'] = datapacquage['commands']['installInit']
        result['postCommandFailure'] = datapacquage['commands']['postCommandFailure']
        result['command'] = datapacquage['commands']['command']

        result['entity_id'] = datapacquage['entity_id']
        result['basepath'] = os.path.dirname(package)
        result['associateinventory'] =datapacquage['inventory']['associateinventory']
        result['licenses'] =datapacquage['inventory']['licenses']
        result['id'] = datapacquage['id']
        result['version'] = datapacquage['version']
        result['label'] = datapacquage['name']
        result['metagenerator'] = datapacquage['metagenerator']
        result['sub_packages'] = datapacquage['sub_packages']
        result['description'] = datapacquage['description']
        result['targetos'] =  datapacquage['targetos']
        result['size'] = str(apimanagepackagemsc.sizedirectory(result['basepath']))
        result['Qversion'] = datapacquage['inventory']['queries']['Qversion']
        result['boolcnd'] = datapacquage['inventory']['queries']['boolcnd']
        result['Qsoftware'] = datapacquage['inventory']['queries']['Qsoftware']
        result['Qvendor'] = datapacquage['inventory']['queries']['Qvendor']
        result['do_reboot'] = 'disable'
        result['files'] = []
        for fich in apimanagepackagemsc.listfilepackage(result['basepath'] ):
            pathfile = os.path.join("/",os.path.basename(os.path.dirname(fich)))
            result['files'].append({"path" : pathfile,
                                    "name" : os.path.basename(fich),
                                    "id" : str(uuid.uuid4()),
                                    "size" : str(os.path.getsize(fich)) })
        return ((result))

    @staticmethod
    def loadpackagelistmsc(login, filter = None, start = None, end = None):
        pending = False
        if "pending" in filter:
            pending = True
        tab = ['description',
               'targetos',
               'sub_packages',
               'entity_id',
               'reboot',
               'version',
               'metagenerator',
               'id',
               'name',
               'basepath',
               'localisation_server',
               'sharing_type']
        result = []
        if login == "root":
            pkgs_shares = PkgsDatabase().pkgs_sharing_admin_profil()
        else:
            pkgs_shares = PkgsDatabase().pkgs_get_sharing_list_login(login)
        _pkgs_shares = {}
        pkgs_share_global = None
        for share in pkgs_shares:
            if share['type'] == "global":
                pkgs_share_global = share
            _pkgs_shares[share['name']] = share

        for packagefiles in apimanagepackagemsc.packagelistmscconfjson(pending):
            obj={}
            try:
                data_file_conf_json = apimanagepackagemsc.readjsonfile(packagefiles)
                if "localisation_server" not in data_file_conf_json:
                    data_file_conf_json['localisation_server'] = pkgs_share_global['name']
                    data_file_conf_json['sharing_type'] = pkgs_share_global['type']
                else:
                    _localisation = data_file_conf_json['localisation_server']
                    data_file_conf_json['sharing_type'] = _pkgs_shares[_localisation]['type']

                if 'filter' in filter:
                    if not (re.search(filter['filter'], data_file_conf_json['name'] , re.IGNORECASE) or
                            re.search(filter['filter'], data_file_conf_json['description'] , re.IGNORECASE) or
                            re.search(filter['filter'], data_file_conf_json['version'] , re.IGNORECASE) or
                            re.search(filter['filter'], data_file_conf_json['targetos'] , re.IGNORECASE) or
                            re.search(filter['filter'], data_file_conf_json['localisation_server'] , re.IGNORECASE) or
                            re.search(filter['filter'], data_file_conf_json['sharing_type'] , re.IGNORECASE)
                            ):
                        continue
                if 'filter1' in filter and \
                    not data_file_conf_json['name'].startswith("Pulse Agent v"):
                    if not (re.search(filter['filter1'], data_file_conf_json['targetos'] , re.IGNORECASE)):
                        continue
                for key in data_file_conf_json:
                    if key in tab:
                        obj[str(key)] = str(data_file_conf_json[key])
                    elif key == 'commands':
                        for z in data_file_conf_json['commands']:
                            obj[str(z)] = str(data_file_conf_json['commands'][z])
                    elif key == 'inventory':
                        for z in data_file_conf_json['inventory']:
                            if z == 'queries':
                                for t in data_file_conf_json['inventory']['queries']:
                                    obj[str(t)] = str(data_file_conf_json['inventory']['queries'][t])
                            else:
                                obj[str(z)] = str(data_file_conf_json['inventory'][z])
                obj['files']=[]
                obj['basepath'] = os.path.dirname(packagefiles)
                obj['size'] = str(apimanagepackagemsc.sizedirectory(obj['basepath']))
                for fich in apimanagepackagemsc.listfilepackage(obj['basepath'] ):
                    pathfile = os.path.join("/",os.path.basename(os.path.dirname(fich)))
                    obj['files'].append({"path" : pathfile,
                                         "name" : os.path.basename(fich),
                                         "id" : str(uuid.uuid4()),
                                         "size" : str(os.path.getsize(fich)) })
                if 'name' in obj:
                    obj['label'] = obj['name']
                obj1 = [obj]
                result.append(obj1)
            except:
                continue

        nb = len(result)
        if start is not None and end is not None:
            return ((nb, result[int(start):int(end) ]))
        else:
            return ((nb, result))

class managepackage:
    exclude_name_package=["sharing", ".stfolder", ".stignore" ]

    @staticmethod
    def packagedir():
        if sys.platform.startswith('linux'):
            return os.path.join("/", "var", "lib", "pulse2", "packages")
        elif sys.platform.startswith('win'):
            return os.path.join(os.environ["ProgramFiles"], "Pulse", "var", "tmp", "packages")
        elif sys.platform.startswith('darwin'):
            return os.path.join("/", "Library", "Application Support", "Pulse", "packages")
        else:
            return None

    @staticmethod
    def listpackages():
        return [os.path.join(managepackage.packagedir(), x) \
            for x in os.listdir(managepackage.packagedir()) \
                if os.path.isdir(os.path.join(managepackage.packagedir(), x)) \
                    and x not in managepackage.exclude_name_package]

    @staticmethod
    def loadjsonfile(filename):
        if os.path.isfile(filename):
            with open(filename, 'r') as info:
                jsonFile = info.read()
            try:
                outputJSONFile = json.loads(jsonFile.decode('utf-8', 'ignore'))
                return outputJSONFile
            except Exception as e:
                logger.error("filename %s error decodage [%s]" % (filename, str(e)))
        return None

    @staticmethod
    def getdescriptorpackagename(packagename):
        for package in managepackage.listpackages():
            try:
                outputJSONFile = managepackage.loadjsonfile(os.path.join(package, "xmppdeploy.json"))
                if 'info' in outputJSONFile \
                        and ('software' in outputJSONFile['info'] and 'version' in outputJSONFile['info']) \
                        and (outputJSONFile['info']['software'] == packagename or outputJSONFile['info']['name'] == packagename):
                    return outputJSONFile
            except Exception as e:
                logger.error("package %s verify format descripttor [%s]" % (package, str(e)))
        return None

    @staticmethod
    def getversionpackagename(packagename):
        for package in managepackage.listpackages():
            print os.path.join(package, "xmppdeploy.json")
            try:
                outputJSONFile = managepackage.loadjsonfile(os.path.join(package, "xmppdeploy.json"))
                if 'info' in outputJSONFile \
                        and ('software' in outputJSONFile['info'] and 'version' in outputJSONFile['info']) \
                        and (outputJSONFile['info']['software'] == packagename or outputJSONFile['info']['name'] == packagename):
                    return outputJSONFile['info']['version']
            except Exception as e:
                logger.error(
                    "package %s verify format descriptor xmppdeploy.json [%s]" % (package, str(e)))
        return None

    @staticmethod
    def getpathpackagename(packagename):
        for package in managepackage.listpackages():
            try:
                outputJSONFile = managepackage.loadjsonfile(os.path.join(package, "xmppdeploy.json"))
                if 'info' in outputJSONFile \
                    and (('software' in outputJSONFile['info'] and outputJSONFile['info']['software'] == packagename)
                         or ('name' in outputJSONFile['info'] and outputJSONFile['info']['name'] == packagename)):
                    return package
            except Exception as e:
                logger.error("package %s missing [%s]" % (package, str(e)))
        return None

    @staticmethod
    def getpathpackagebyuuid(uuidpackage):
        """
        This function is used to find the package based on the uuid
        Args:
            uuidpackage: The uuid of the package we are searching
        Returns:
            We return the package, it returns None if any error or if
                the package is not found.
        """
        for package in managepackage.listpackages():
            try:
                outputJSONFile = managepackage.loadjsonfile(
                    os.path.join(package, "conf.json"))
                if 'id' in outputJSONFile and outputJSONFile['id'] == uuidpackage:
                    return package
            except Exception as e:
                logger.error("The conf.json for the package %s is missing" % package)
                logger.error("we are encountering the error: %s"  % str(e))
                return None
        logger.error("We did not find the package %s" % package)
        return None

    @staticmethod
    def getversionpackageuuid(packageuuid):
        """
        This function is used to find the version of the package based
            on the uuid
        Args:
            packageuuid: The uuid of the package we are searching
        Returns:
            We return the version of package, it returns None if
                any error or if the package is not found.
        """
        for package in managepackage.listpackages():
            try:
                outputJSONFile = managepackage.loadjsonfile(
                    os.path.join(package, "conf.json"))
                if 'id' in outputJSONFile and outputJSONFile['id'] == packageuuid \
                    and 'version' in outputJSONFile:
                    return outputJSONFile['version']
            except Exception as e:
                logger.error(
                    "package %s verify format descriptor conf.json [%s]" %
                    (packageuuid, str(e)))
        logger.error("package %s verify version" \
                        "in descriptor conf.json [%s]" %(packageuuid))
        return None

    @staticmethod
    def getnamepackagefromuuidpackage(uuidpackage):
        pathpackage = os.path.join(managepackage.packagedir(), uuidpackage, "xmppdeploy.json")
        if os.path.isfile(pathpackage):
            outputJSONFile = managepackage.loadjsonfile(pathpackage)
            return outputJSONFile['info']['name']
        return None

    @staticmethod
    def getdescriptorpackageuuid(packageuuid):
        xmppdeployFile = os.path.join(managepackage.packagedir(), packageuuid, "xmppdeploy.json")
        if os.path.isfile(xmppdeployFile):
            try:
                outputJSONFile = managepackage.loadjsonfile(xmppdeployFile)
                return outputJSONFile
            except Exception:
                return None

    @staticmethod
    def getpathpackage(uuidpackage):
        return os.path.join(managepackage.packagedir(), uuidpackage)


class search_list_of_deployment_packages:
    """
        Recursively search for all dependencies for this package
    """

    def __init__(self, packageuuid):
        self.list_of_deployment_packages = set()
        self.packageuuid = packageuuid

    def search(self):
        self.__recursif__(self.packageuuid)
        return self.list_of_deployment_packages

    def __recursif__(self, packageuuid):
        self.list_of_deployment_packages.add(packageuuid)
        objdescriptor = managepackage.getdescriptorpackageuuid(packageuuid)
        if objdescriptor is not None:
            ll = self.__list_dependence__(objdescriptor)
            for y in ll:
                if y not in self.list_of_deployment_packages:
                    self.__recursif__(y)

    def __list_dependence__(self, objdescriptor):
        if objdescriptor is not None and \
            'info' in objdescriptor and \
                'Dependency' in objdescriptor['info']:
            return objdescriptor['info']['Dependency']
        else:
            return []
