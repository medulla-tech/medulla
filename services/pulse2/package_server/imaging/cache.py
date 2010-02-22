# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Caching related functions / objects
"""

import logging
import ConfigParser
import os.path

import pulse2.utils
import pulse2.package_server.config

class UUIDCache(pulse2.utils.Singleton):
    """
    This is a object-cache for UUID/MAC conversion stuff.

    It work like this:
     - if info is in cache *and* less than memoryLifetime, serve it
     - if not, try to find it into the local cache (UUIDS.txt); it less than diskLifetime, serve it and update local cache, resetting lifetime
     - if not, try to find it asking the agent, updating both disk cache and local cache, resetting lifetime
    """

    cachePath = pulse2.package_server.config.P2PServerCP().imaging_api['uuid_cache_file']
    log = logging.getLogger()
    log.info("Using %s as UUID Cache File" % cachePath)
    config = ConfigParser.ConfigParser()

    def __init__(self):
        if not os.path.isfile(self.cachePath):
            try:
                fd = open(self.cachePath, 'wb')
                fd.close()
            except Exception, e:
                self.log.warn("Can't create my UUID Cache File %s " % self.cachePath)
                return False
        self.config.read(self.cachePath)

    def _flush(self):
        # update cache file using our memory stucture
            try:
                fd = open(self.cachePath, 'wb')
                self.config.write(fd)
                fd.close()
            except Exception, e:
                self.log.warn("Can't create my UUID Cache File %s " % cachePath)
                return False

    def get(self, mac):
        if self.config.has_section(mac):
            if self.config.has_option(mac,'uuid'):
                return self.config.get(mac, 'uuid')
        return False

    def set(self, mac, uuid):
        if not self.config.has_section(mac):
            self.config.add_section(mac)
        self.config.set(mac, 'uuid', uuid)
        self._flush()
