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

from pulse2.package_server.assign_algo import MMAssignAlgo
from pulse2.database.imaging import ImagingDatabase
from urlparse import urlparse

class MMUserAssignAlgo(MMAssignAlgo):
    name = 'multi_site'
    assign = {}

    def getMachineMirror(self, m):
        self.logger = logging.getLogger()
        self.logger.debug("######### INITIALISATION getMachineMirror ##########")
        self.logger.debug("######### database %s" % ImagingDatabase())
        machine = Machine().from_h(m)
        if not machine.uuid in self.assign:
            self.assign[machine.uuid] = {}
        if not 'getMirror' in self.assign[machine.uuid]:
            self.logger.debug("######### uuid %s" % machine.uuid)
            # Get url corresponding to the imaging server of this machine
            entity_id = ImagingDatabase().getTargetsEntity([machine.uuid])[0]
            self.logger.debug("######### entity_id %s" % entity_id)
            url = ImagingDatabase().getEntityUrl(entity_id.uuid)
            self.logger.debug("######### url %s" % url)
            # Extract the hostname or ipaddress from the url
            server = urlparse(url).hostname
            self.logger.debug("######### server %s" % server)
            # Replace the server value
            self.assign[machine.uuid]['getMirror'] = self.mirrors[random.randint(0,len(self.mirrors)-1)].toH()
            self.assign[machine.uuid]['getMirror']['server'] = server
        self.logger.debug("######### Return %s" % self.assign[machine.uuid]['getMirror'])
        return self.assign[machine.uuid]['getMirror']

    def getMachineMirrorFallback(self, m): # To be done
        return 0

    def getMachinePackageApi(self, m):
        self.logger = logging.getLogger()
        self.logger.debug("######### INITIALISATION getMachinePackageApi ##########")
        self.logger.debug("######### database %s" % ImagingDatabase())
        machine = Machine().from_h(m)
        if not machine.uuid in self.assign:
            self.assign[machine.uuid] = {}
        if not 'getMachinePackageApi' in self.assign[machine.uuid]:
            self.logger.debug("######### uuid %s" % machine.uuid)
            # Get url corresponding to the imaging server of this machine
            result = ImagingDatabase().getTargetPackageServer(machine.uuid)
            self.logger.debug("######### url %s" % result[0].url)
            # Extract the hostname or ipaddress from the url
            server = urlparse(result[0].url).hostname
            self.logger.debug("######### server %s" % server)
            # Get the package apis and replace the server value
            self.assign[machine.uuid]['getMachinePackageApi'] = []
            self.assign[machine.uuid]['getMachinePackageApi'] += map(lambda papi: papi.toH(), self.package_apis)
            for api in xrange(len(self.assign[machine.uuid]['getMachinePackageApi'])):
                self.assign[machine.uuid]['getMachinePackageApi'][api]['server'] = server
        self.logger.debug("######### Return %s" % self.assign[machine.uuid]['getMachinePackageApi'])
        return self.assign[machine.uuid]['getMachinePackageApi']
