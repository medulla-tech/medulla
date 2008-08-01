#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id: __init__.py 30 2008-02-08 16:40:54Z nrueff $
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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

"""
    Pulse2 PackageServer
"""

import logging
from pulse2.package_server.utilities import Singleton
from distutils.sysconfig import get_python_lib
import imp
import os

class AssignAlgo(Singleton):
    def init(self, mirrors, mirrors_fallback, package_apis):
        self.logger = logging.getLogger()
        self.mirrors = mirrors
        self.mirrors_fallback = mirrors_fallback
        self.package_apis = package_apis
        
    def getMachineMirror(self, machine):
        raise Exception("not defined")

    def getMachineMirrorFallback(self, machine):
        raise Exception("not defined")

    def getMachinePackageApi(self, machine):
        raise Exception("not defined")

class AssignAlgoManager(Singleton):
    def getAlgo(self, assign_algo):
        algo, assign_algo = self._getAlgo(assign_algo)
        logging.getLogger().debug("Using the %s Assign Algorythm"%(assign_algo))
        return algo
    
    def _getAlgo(self, assign_algo):
        try:
            if os.name == 'nt':
                curdir = os.path.dirname(__file__)
                if curdir.endswith("library.zip"):
                    searchpath = os.path.dirname(curdir)
                else:
                    # Go to the parent directory
                    searchpath, _ = os.path.split(curdir)
                    # And enter assign_algo directory
                    searchpath = os.path.join(searchpath, 'assign_algo')
            else:
                searchpath = os.path.join(get_python_lib(), 'pulse2', 'package_server', 'assign_algo')
            logging.getLogger().debug("Algo search path: %s" % searchpath)
            f, p, d = imp.find_module(assign_algo, [searchpath])
            mod = imp.load_module('MyAssignAlgo', f, p, d)
            ret = mod.UserAssignAlgo()
        except Exception, e:
            if assign_algo != 'default':
                assign_algo = 'default'
                ret, assign_algo = self._getAlgo(assign_algo)
            else:
                logging.getLogger().error("Cant load any Assign Algorythm")
                ret = None
        return (ret, assign_algo)
