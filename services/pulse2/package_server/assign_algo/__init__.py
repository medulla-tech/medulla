#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
    Pulse2 PackageServer
"""

import logging
import pulse2.utils
import imp
import os


class MMAssignAlgo(pulse2.utils.Singleton):
    def init(
        self,
        mirrors,
        mirrors_fallback,
        package_apis,
        url2mirrors,
        url2mirrors_fallback,
        url2package_apis,
    ):
        self.logger = logging.getLogger()
        self.mirrors = mirrors
        self.mirrors_fallback = mirrors_fallback
        self.package_apis = package_apis
        self.url2mirrors = url2mirrors
        self.url2mirrors_fallback = url2mirrors_fallback
        self.url2package_apis = url2package_apis

    def getMachineMirror(self, machine):
        raise Exception("getMachineMirror not defined")

    def getMachineMirrorFallback(self, machine):
        raise Exception("getMachineMirrorFallback not defined")

    def getMachinePackageApi(self, machine):
        raise Exception("getMachinePackageApi not defined")


class UPAssignAlgo(pulse2.utils.Singleton):
    def init(self, package_api_put):
        self.logger = logging.getLogger()
        self.package_api_put = [x.toH() for x in package_api_put]

    def getUserPackageApi(self, user):
        raise Exception("getUserPackageApi not defined")


class IntAssignAlgoManager(pulse2.utils.Singleton):
    name = ""

    def getAlgo(self, assign_algo):
        wanted = assign_algo
        algo, assign_algo = self._getAlgo(assign_algo)
        logging.getLogger().debug(
            "Using the %s %s Assign Algorythm" % (assign_algo, self.name)
        )
        if wanted != assign_algo:
            logging.getLogger().warning(
                "Can't load the wanted one (conf:%s, use:%s)" % (wanted, assign_algo)
            )
        return algo

    def _getAlgo(self, assign_algo):
        try:
            if os.name == "nt":
                curdir = os.path.dirname(__file__)
                if "library.zip" in curdir:
                    # When we are runnning standalone (py2exe output)
                    # Go to our container directory
                    searchpath, _ = curdir.split("library.zip")
                else:
                    # When running with the source tree
                    # Go to the parent directory
                    searchpath, _ = os.path.split(curdir)
                # And enter assign_algo directory
                searchpath = os.path.join(searchpath, "assign_algo")
            else:
                searchpath = os.path.dirname(__file__)
            logging.getLogger().debug("Algo search path: %s" % searchpath)
            f, p, d = imp.find_module(assign_algo, [searchpath])
            mod = imp.load_module("MyAssignAlgo", f, p, d)
            ret = self.getClassInModule(mod)
        except Exception as e:
            logging.getLogger().debug(e)
            if assign_algo != "default":
                assign_algo = "default"
                ret, assign_algo = self._getAlgo(assign_algo)
            else:
                logging.getLogger().error(
                    "Cant load any %s Assign Algorythm" % (self.name)
                )
                ret = None
        return (ret, assign_algo)

    def getClassInModule(self, mod):
        raise Exception("getClassInModule not defined")


class MMAssignAlgoManager(IntAssignAlgoManager):
    name = "Machine/Mirrors"

    def getClassInModule(self, mod):
        return mod.MMUserAssignAlgo()


class UPAssignAlgoManager(IntAssignAlgoManager):
    name = "User/PackagePut"

    def getClassInModule(self, mod):
        return mod.UPUserAssignAlgo()
