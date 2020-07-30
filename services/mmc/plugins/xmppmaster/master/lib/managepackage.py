#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    @staticmethod
    def readjsonfile(namefile):
        with open(namefile) as json_data:
            data_dict = json.load(json_data)
        return data_dict

    @staticmethod
    def packagelistmsc():
        folderpackages = os.path.join("/", "var" ,"lib","pulse2","packages")
        return [ os.path.join(folderpackages,x) for x in os.listdir(folderpackages) \
            if os.path.isdir(os.path.join(folderpackages,x)) \
                and str(os.path.join(folderpackages,x))[-9:] != ".stfolder" ]

    @staticmethod
    def listfilepackage(folderpackages):
        return [ os.path.join(folderpackages,x) for x in os.listdir(folderpackages) \
            if not os.path.isdir(os.path.join(folderpackages,x)) \
            and str(os.path.join(folderpackages,x))[-9:] != ".stfolder"]

    @staticmethod
    def packagelistmscconfjson(pending = False):
        folderpackages = os.path.join("/", "var" ,"lib","pulse2","packages")
        listfichierconf =  [ os.path.join(folderpackages,x,"conf.json") \
            for x in os.listdir(folderpackages) \
                if os.path.isdir(os.path.join(folderpackages,x)) \
                    and str(os.path.join(folderpackages,x))[-9:] != ".stfolder" ]
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
        result['size'] = apimanagepackagemsc.sizedirectory(result['basepath'])
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
                                    "size" : os.path.getsize(fich) })
        return ((result))

    @staticmethod
    def loadpackagelistmsc(filter = None, start = None, end = None):
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
               'basepath']
        result = []

        for packagefiles in apimanagepackagemsc.packagelistmscconfjson(pending):
            obj={}
            data_file_conf_json = apimanagepackagemsc.readjsonfile(packagefiles)
            if 'filter' in filter:
                if not (re.search(filter['filter'], data_file_conf_json['name'] , re.IGNORECASE) or
                        re.search(filter['filter'], data_file_conf_json['description'] , re.IGNORECASE) or
                        re.search(filter['filter'], data_file_conf_json['version'] , re.IGNORECASE) or
                        re.search(filter['filter'], data_file_conf_json['targetos'] , re.IGNORECASE)):
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
            obj['size'] = apimanagepackagemsc.sizedirectory(obj['basepath'])
            for fich in apimanagepackagemsc.listfilepackage(obj['basepath'] ):
                pathfile = os.path.join("/",os.path.basename(os.path.dirname(fich)))
                obj['files'].append({"path" : pathfile,
                                     "name" : os.path.basename(fich),
                                     "id" : str(uuid.uuid4()),
                                     "size" : os.path.getsize(fich) })
            if 'name' in obj:
                obj['label'] = obj['name']
            obj1 = [obj]
            result.append(obj1)

        nb = len(result)
        if start is not None and end is not None:
            return ((nb, result[int(start):int(end) ]))
        else:
            return ((nb, result))

class managepackage:
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
                    and str(os.path.join(managepackage.packagedir(), x))[-9:] != ".stfolder"]

    @staticmethod
    def loadjsonfile(filename):
        if os.path.isfile(filename):
            with open(filename, 'r') as info:
                dd = info.read()
            try:
                jr = json.loads(dd.decode('utf-8', 'ignore'))
                return jr
            except Exception as e:
                logger.error("filename %s error decodage [%s]" % (filename, str(e)))
        return None

    @staticmethod
    def getdescriptorpackagename(packagename):
        for package in managepackage.listpackages():
            try:
                jr = managepackage.loadjsonfile(os.path.join(package, "xmppdeploy.json"))
                if 'info' in jr \
                        and ('software' in jr['info'] and 'version' in jr['info']) \
                        and (jr['info']['software'] == packagename or jr['info']['name'] == packagename):
                    return jr
            except Exception as e:
                logger.error("package %s verify format descripttor [%s]" % (package, str(e)))
        return None

    @staticmethod
    def getversionpackagename(packagename):
        for package in managepackage.listpackages():
            print os.path.join(package, "xmppdeploy.json")
            try:
                jr = managepackage.loadjsonfile(os.path.join(package, "xmppdeploy.json"))
                if 'info' in jr \
                        and ('software' in jr['info'] and 'version' in jr['info']) \
                        and (jr['info']['software'] == packagename or jr['info']['name'] == packagename):
                    return jr['info']['version']
            except Exception as e:
                logger.error(
                    "package %s verify format descriptor xmppdeploy.json [%s]" % (package, str(e)))
        return None

    @staticmethod
    def getpathpackagename(packagename):
        for package in managepackage.listpackages():
            try:
                jr = managepackage.loadjsonfile(os.path.join(package, "xmppdeploy.json"))
                if 'info' in jr \
                    and (('software' in jr['info'] and jr['info']['software'] == packagename)
                         or ('name' in jr['info'] and jr['info']['name'] == packagename)):
                    return package
            except Exception as e:
                logger.error("package %s missing [%s]" % (package, str(e)))
        return None

    @staticmethod
    def getnamepackagefromuuidpackage(uuidpackage):
        pathpackage = os.path.join(managepackage.packagedir(), uuidpackage, "xmppdeploy.json")
        if os.path.isfile(pathpackage):
            jr = managepackage.loadjsonfile(pathpackage)
            return jr['info']['name']
        return None

    @staticmethod
    def getdescriptorpackageuuid(packageuuid):
        file = os.path.join(managepackage.packagedir(), packageuuid, "xmppdeploy.json")
        if os.path.isfile(file):
            try:
                jr = managepackage.loadjsonfile(file)
                return jr
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
