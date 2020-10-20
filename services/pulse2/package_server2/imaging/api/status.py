# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: __init__.py 5378 2010-02-16 14:09:38Z nrueff $
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
Pulse 2 Package Server Imaging API status class.
"""

import logging
import os

from twisted.internet.utils import getProcessOutput

class Status:

    """
    Class that allows to get the status of the imaging service.
    """

    def __init__(self, config):
        self.logging = logging.getLogger()
        self.config = config
        self.ret = {}

    def get(self):
        d = getProcessOutput('/bin/df', ['-m'], { 'LANG' : 'C', 'LANGUAGE' : 'C'})
        d.addCallback(self.getAvailableSpaceOk)
        d.addErrback(self.getAvailableSpaceErr)
        return d

    def getAvailableSpaceOk(self, result):
        for line in result.split('\n'):
            words = line.split()
            # Last column should contain the mounted on part
            try:
                mount = words[-1]
            except IndexError:
                continue
            if os.path.join(self.config.imaging_api['base_folder'], self.config.imaging_api['masters_folder']).startswith(mount):
                try:
                    self.ret['space_available'] = (int(words[-2].rstrip('%')), int(words[-3]) )
                except (ValueError, IndexError):
                    pass
                # Don't break but continue because mount maybe /, which
                # will always match
        self.getMemoryInformations()

    def getAvailableSpaceErr(self, error):
        self.logging.error(error)
        self.ret['space_available'] = (-1, -1)
        self.getMemoryInformations()

    def getMemoryInformations(self):
        d = getProcessOutput('free', { 'LANG' : 'C', 'LANGUAGE' : 'C'})
        d.addCallback(self.getMemoryInformationsOk)
        d.addErrback(self.getMemoryInformationsErr)

    def getMemoryInformationsOk(self, result):
        self.ret['mem_info'] = result.split('\n')
        self.getDiskInformations()

    def getMemoryInformationsErr(self, error):
        self.logging.error(error)
        self.ret['mem_info'] = -1
        self.getDiskInformations()

    def getDiskInformations(self):
        d = getProcessOutput('/bin/df', ['-k'], { 'LANG' : 'C', 'LANGUAGE' : 'C'})
        d.addCallback(self.getDiskInformationsOk)
        d.addErrback(self.getDiskInformationsErr)

    def getDiskInformationsOk(self, result):
        self.ret['disk_info'] = result.split('\n')
        self.getUptime()

    def getDiskInformationsErr(self, error):
        self.logging.error(error)
        self.ret['disk_info'] = -1
        self.getUptime()

    def getUptime(self):
        try:
            f = file('/proc/uptime')
            data = f.read()
            f.close()
        except Exception, e:
            self.logging.error(e)
            data = -1
        self.ret['uptime'] = data
        self.getStats()

    def getStats(self):
        self.ret['stats'] = {}
        # TODO need to get that information from internals
        self.ret['stats']['rescue'] = 0
        self.ret['stats']['master'] = 0
        self.ret['stats']['total'] = 0
        self.returnResult()

    def returnResult(self):
        self.deferred.callback(self.ret)
