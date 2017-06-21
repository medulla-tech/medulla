#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os,platform
import os.path
import json
import logging

logger = logging.getLogger()


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
            except:
                logger.error("filename %s error decodage"%filename)
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
            Except Exception:
                logger.error("package %s verify format descripttor"%package)
        return None

    @staticmethod
    def getversionpackagename(packagename):
        for package in managepackage.listpackages():
            print os.path.join(t,"xmppdeploy.json")
            try:
                jr = managepackage.loadjsonfile(os.path.join(package,"xmppdeploy.json"))
                if 'info' in jr \
                    and ('software' in jr['info'] and 'version'  in jr['info']) \
                    and (jr['info']['software'] == packagename or jr['info']['name'] == packagename):
                    return jr['info']['version']
            except Exception:
                logger.error("package %s verify format descriptor xmppdeploy.json"%package)
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
            except :
                 logger.error("package %s missing"%package)
                return None
        return None
    
    
    @staticmethod
    def getnamepackagefromuuidpackage(uuidpackage):
        pathpackage = os.path.join(managepackage.packagedir(),uuidpackage,"xmppdeploy.json")
        if os.path.isfile(pathpackage):
            jr = managepackage.loadjsonfile(pathpackage)
            return jr['info']['name']
        return None


#class managepackagefile:
    #def __init__():
        #pass
    
    #def organisation_list():
        #return listorganisation
    
    #def list_package_for_organisation(organisation):    
        #pass
    
    ######################
    #def add_package_organisation(idpackage, organisation):
    
    #def create_xmpp_descriptor_organisation()
    
    
    
