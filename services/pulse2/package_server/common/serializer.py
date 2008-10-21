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

import pickle
import os
import logging
from pulse2.package_server.utilities import Singleton

class PkgsRsyncStateSerializer(Singleton):
    def init(self, common):
        self.logger = logging.getLogger()
        self.logger.debug("PkgsRsyncStateSerializer is initializing")
        self.common = common
        self.config = common.config
        self.filename = self.config.package_mirror_status_file
        return self.unserialize()

    def serialize(self):
        self.logger.debug("PkgsRsyncStateSerializer serialize")
        # will serialize self.common.dontgivepkgs into file
        try:
            file = open(self.filename, 'w')
            pickle.dump(self.common.dontgivepkgs, file)
            file.close()
        except:
            self.logger.debug("PkgsRsyncStateSerializer serialize failed")
            return False
        self.logger.debug("PkgsRsyncStateSerializer serialize succeed")
        return True

    def unserialize(self):
        self.logger.debug("PkgsRsyncStateSerializer unserialize")
        # will unserialize file into self.common.dontgivepkgs
        try:
            if not os.path.exists(self.filename):
                return False
            file = open(self.filename, 'r')
            r = pickle.load(file)
            file.close()
            if type(r) == dict:
                self.common.dontgivepkgs = r
                self.logger.debug("PkgsRsyncStateSerializer unserialize succeed")
                return True
            self.logger.debug("PkgsRsyncStateSerializer unserialize failed")
            return False
        except:
            self.logger.debug("PkgsRsyncStateSerializer unserialize failed")
            return False
    

