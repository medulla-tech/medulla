#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
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
    Pulse2 Scheduler
"""

import logging
from pulse2.utils import Singleton
import imp
import os

class MGAssignAlgo(Singleton):
    def __init__(self):
        self.logger = logging.getLogger()
        Singleton.__init__(self)

    def getMachineGroup(self, myT):
        raise Exception("getMachineGroup not defined")

    def getMaxNumberOfGroups(self):
        raise Exception("getMaxNumberOfGroups not defined")

class IntAssignAlgoManager(Singleton):
    name = ''
    def setAlgo(self, assign_algo):
        wanted = assign_algo
        algo, assign_algo = self._getAlgo(assign_algo)
        logging.getLogger().debug("Using the %s %s Assign Algorithm"%(assign_algo, self.name))
        if wanted != assign_algo:
            logging.getLogger().warning("Can't load the wanted one (conf:%s, use:%s)"%(wanted, assign_algo))
        self.algo = algo

    def _getAlgo(self, assign_algo):
        try:
            if os.name == 'nt':
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
                searchpath = [os.path.join(searchpath, 'assign_algo')]
            else:
                import sys
                searchpath = map (lambda x: os.path.join(x, 'pulse2', 'scheduler', 'assign_algo'), sys.path)
            logging.getLogger().debug("Algo search path: %s" % ':'.join(searchpath))
            f, p, d = imp.find_module(assign_algo, searchpath)
            mod = imp.load_module('MyAssignAlgo', f, p, d)
            ret = self.getClassInModule(mod)
        except Exception, e:
            logging.getLogger().warn("while loading Assign Algo: %s" % e)
            if assign_algo != 'default':
                assign_algo = 'default'
                ret, assign_algo = self._getAlgo(assign_algo)
            else:
                logging.getLogger().error("Cant load any %s Assign Algorithm"%(self.name))
                ret = None
        return (ret, assign_algo)

    def getClassInModule(self, mod):
        raise Exception("getClassInModule not defined")

class MGAssignAlgoManager(IntAssignAlgoManager):
    name = 'Machine/Group'
    def getClassInModule(self, mod):
        return mod.MGUserAssignAlgo()

    def getMachineGroup(self, myT):
        return self.algo.getMachineGroup(myT)

    def getMaxNumberOfGroups(self):
        return self.algo.getMaxNumberOfGroups()

