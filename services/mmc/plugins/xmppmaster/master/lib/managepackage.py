#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import os.path
import json
import logging

logger = logging.getLogger()


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
        return [os.path.join(managepackage.packagedir(), x) for x in os.listdir(managepackage.packagedir()) if os.path.isdir(os.path.join(managepackage.packagedir(), x))]

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
            # print ll
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
