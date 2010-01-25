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
    Pulse2 PackageServer
"""

import twisted.web.xmlrpc
import logging
import random
from pulse2.package_server.types import Machine
from pulse2.package_server.xmlrpc import MyXmlrpc

class SchedulerApi(MyXmlrpc):
    type = 'SchedulerApi'
    def __init__(self, name, config):
        MyXmlrpc.__init__(self)
        self.name = name
        self.config = config
        self.logger = logging.getLogger()
        self.assign = {}
        if self.config.has_key('schedulers'):
            self.schedulers = self.config['schedulers'].split(' ')
        else:
            self.schedulers = ['']
        self.logger.info("(%s) %s : initialised"%(self.type, self.name))

    def xmlrpc_getServerDetails(self):
        return self.config

    def xmlrpc_getScheduler(self, m):
        machine = Machine().from_h(m)
        if not self.assign.has_key(machine.uuid):
            self.assign[machine.uuid] = self.schedulers[random.randint(0,len(self.schedulers)-1)]
        return self.assign[machine.uuid]

    def xmlrpc_getSchedulers(self, machines):
        ret = []
        for m in machines:
            machine = Machine().from_h(m)
            if not self.assign.has_key(machine.uuid):
                self.assign[machine.uuid] = self.schedulers[random.randint(0,len(self.schedulers)-1)]
            ret.append(self.assign[machine.uuid])
        return ret

