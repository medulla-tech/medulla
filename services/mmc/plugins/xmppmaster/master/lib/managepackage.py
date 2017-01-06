#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os,platform
import os.path
import json


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
                print "Decoding error"
                pass
        return None

    @staticmethod
    def getdescriptorpackagename(packagename):
        for t in managepackage.listpackages():
            print os.path.join(t,"xmppdeploy.json")
            jr = managepackage.loadjsonfile(os.path.join(t,"xmppdeploy.json"))
            if 'info' in jr \
                and ('software' in jr['info'] and 'version'  in jr['info']) \
                and (jr['info']['software'] == packagename or jr['info']['name'] == packagename):
                return jr
        return None

    @staticmethod
    def getversionpackagename(packagename):
        for t in managepackage.listpackages():
            print os.path.join(t,"xmppdeploy.json")
            jr = managepackage.loadjsonfile(os.path.join(t,"xmppdeploy.json"))
            if 'info' in jr \
                and ('software' in jr['info'] and 'version'  in jr['info']) \
                and (jr['info']['software'] == packagename or jr['info']['name'] == packagename):
                return jr['info']['version']
        return None

    @staticmethod
    def getpathpackagename(packagename):
        for t in managepackage.listpackages():
            print t
            print os.path.join(t,"xmppdeploy.json")
            jr = managepackage.loadjsonfile(os.path.join(t,"xmppdeploy.json"))
            if 'info' in jr \
                and (('software' in jr['info'] and jr['info']['software'] == packagename )\
                or ( 'name'  in jr['info'] and  jr['info']['name'] == packagename)):
                return t
        return None
