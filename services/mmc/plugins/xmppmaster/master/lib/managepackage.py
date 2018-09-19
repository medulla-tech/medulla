#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
import sys, os
import os.path
import json
import logging
from utils import md5, simplecommand
from pulse2.database.xmppmaster import XmppMasterDatabase
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
        return [ os.path.join(folderpackages,x) for x in os.listdir(folderpackages) if os.path.isdir(os.path.join(folderpackages,x)) and str(os.path.join(folderpackages,x))[-9:] != ".stfolder" ]

    @staticmethod
    def listfilepackage(folderpackages):
        return [ os.path.join(folderpackages,x) for x in os.listdir(folderpackages) if not os.path.isdir(os.path.join(folderpackages,x)) ]

    @staticmethod
    def packagelistmscconfjson(pending = False):
        folderpackages = os.path.join("/", "var" ,"lib","pulse2","packages")
        listfichierconf =  [ os.path.join(folderpackages,x,"conf.json") for x in os.listdir(folderpackages) if os.path.isdir(os.path.join(folderpackages,x)) and str(os.path.join(folderpackages,x))[-9:] != ".stfolder" ]
        listpackagependig = XmppMasterDatabase().list_pending_synchro_package()
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
                if not (filter['filter'] in data_file_conf_json['name'] or 
                   filter['filter'] in data_file_conf_json['description'] or 
                   filter['filter'] in data_file_conf_json['version'] or
                   filter['filter'] in data_file_conf_json['targetos']):
                    continue
            if 'filter1' in filter and \
                not data_file_conf_json['name'].startswith("Pulse Agent v"):
                if not (filter['filter1'] in data_file_conf_json['targetos']):
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
            return os.path.join("/", "var" ,"lib","pulse2","packages")
        elif sys.platform.startswith('win'):
            return os.path.join(os.environ["ProgramFiles"], "Pulse","var","tmp","packages")
        elif sys.platform.startswith('darwin'):
            return os.path.join("/", "Library", "Application Support", "Pulse", "packages")
        else:
            return None

    @staticmethod
    def listpackages():
        return [ os.path.join(managepackage.packagedir(),x) for x in os.listdir(managepackage.packagedir()) if os.path.isdir(os.path.join(managepackage.packagedir(),x)) ]

    @staticmethod
    def loadjsonfile(filename):
        if os.path.isfile(filename ):
            with open(filename,'r') as info:
                dd = info.read()
            try:
                jr= json.loads(dd.decode('utf-8', 'ignore'))
                return jr
            except Exception as e:
                logger.error("filename %s error decodage [%s]"%(filename ,str(e)))
        return None

    @staticmethod
    def getdescriptorpackagename(packagename):
        for package in managepackage.listpackages():
            try:
                jr = managepackage.loadjsonfile(os.path.join(package,"xmppdeploy.json"))
                if 'info' in jr \
                    and ('software' in jr['info'] and 'version'  in jr['info']) \
                    and (jr['info']['software'] == packagename or jr['info']['name'] == packagename):
                    return jr
            except Exception as e:
                logger.error("package %s verify format descripttor [%s]"%(package,str(e)))
        return None

    @staticmethod
    def getversionpackagename(packagename):
        for package in managepackage.listpackages():
            print os.path.join(package,"xmppdeploy.json")
            try:
                jr = managepackage.loadjsonfile(os.path.join(package,"xmppdeploy.json"))
                if 'info' in jr \
                    and ('software' in jr['info'] and 'version'  in jr['info']) \
                    and (jr['info']['software'] == packagename or jr['info']['name'] == packagename):
                    return jr['info']['version']
            except Exception as e:
                logger.error("package %s verify format descriptor xmppdeploy.json [%s]"%(package,str(e)))
        return None

    @staticmethod
    def getpathpackagename(packagename):
        for package in managepackage.listpackages():
            try:
                jr = managepackage.loadjsonfile(os.path.join(package,"xmppdeploy.json"))
                if 'info' in jr \
                    and (('software' in jr['info'] and jr['info']['software'] == packagename )\
                    or ( 'name'  in jr['info'] and  jr['info']['name'] == packagename)):
                    return package
            except Exception as e:
                logger.error("package %s missing [%s]"%(package,str(e)))
        return None

    @staticmethod
    def getnamepackagefromuuidpackage(uuidpackage):
        pathpackage = os.path.join(managepackage.packagedir(),uuidpackage,"xmppdeploy.json")
        if os.path.isfile(pathpackage):
            jr = managepackage.loadjsonfile(pathpackage)
            return jr['info']['name']
        return None

    @staticmethod
    def getdescriptorpackageuuid(packageuuid):
        file = os.path.join(managepackage.packagedir(),packageuuid,"xmppdeploy.json")
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
        self.__recursif__(self.packageuuid )
        return self.list_of_deployment_packages

    def __recursif__(self, packageuuid ):
        self.list_of_deployment_packages.add(packageuuid)
        objdescriptor = managepackage.getdescriptorpackageuuid(packageuuid)
        if objdescriptor is not None:
            ll = self.__list_dependence__(objdescriptor)
            for y in ll:
                if y not in  self.list_of_deployment_packages:
                    self.__recursif__(y)

    def __list_dependence__(self, objdescriptor):
        if objdescriptor is not None and \
            'info' in objdescriptor and \
                'Dependency' in objdescriptor['info']:
            return objdescriptor['info']['Dependency']
        else:
            return []


