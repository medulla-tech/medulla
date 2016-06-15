#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2016 Siveo, http://www.siveo.net
#
# $Id$
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

"""
    Pulse2 PackageServer
"""

import logging
from twisted.internet import  defer
from pulse2.package_server.assign_algo import MMAssignAlgo
from urlparse import urlparse
from pulse2.package_server.imaging.api.functions import Imaging

class MMUserAssignAlgo(MMAssignAlgo):
    name = 'multi_site'
    assign = {}

    def getMachineMirror(self, m):
        server=''
        machine = Machine().from_h(m)
        if not machine.uuid in self.assign:
            self.assign[machine.uuid] = {}
        if not 'getMirror' in self.assign[machine.uuid]:
            if 'server' in m:
                server = m['server']
                logging.getLogger().debug("algo multi_site machine :[ %s ] pserver : (ip : %s name : '%s'] Entity : [ %s ]"%(m['uuid'], m['server'], m['servernane'], m['serveruuid'], m['entity']))
            # Replace the server value
            self.assign[machine.uuid]['getMirror'] = self.mirrors[random.randint(0,len(self.mirrors)-1)].toH()
            self.assign[machine.uuid]['getMirror']['server'] = server
        return self.assign[machine.uuid]['getMirror']

    def getMachineMirrorFallback(self, m): # To be done
        return 0

    def getMachinePackageApi(self, m):
        server = ''
        machine = Machine().from_h(m)
        if not machine.uuid in self.assign:
            self.assign[machine.uuid] = {}
        if not 'getMachinePackageApi' in self.assign[machine.uuid]:
            #ip server corresponding to the imaging server of this machine
            if 'server' in m:
                server = m['server']
                logging.getLogger().debug("algo multi_site machine :[ %s ] pserver : (ip : %s name : '%s']"%(m['uuid'], m['server'], m['servernane'], m['serveruuid']))
            # Get the package apis and replace the server value
            self.assign[machine.uuid]['getMachinePackageApi'] = []
            self.assign[machine.uuid]['getMachinePackageApi'] += map(lambda papi: papi.toH(), self.package_apis)
            for api in xrange(len(self.assign[machine.uuid]['getMachinePackageApi'])):
                self.assign[machine.uuid]['getMachinePackageApi'][api]['server'] = server
        return self.assign[machine.uuid]['getMachinePackageApi']
