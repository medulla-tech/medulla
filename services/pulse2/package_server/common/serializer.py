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

import pickle
import os
import logging
import pulse2.utils

class PkgsRsyncStateSerializer(pulse2.utils.Singleton):
    def init(self, common):
        self.logger = logging.getLogger()
        self.logger.debug("Package synchro state serialization, is initializing")
        self.common = common
        self.config = common.config
        self.filename = self.config.package_mirror_status_file
        return self.unserialize()

    def serialize(self):
        self.logger.debug("Package synchro state serialization, serialize")
        # will serialize self.common.dontgivepkgs into file
        try:
            file = open(self.filename, 'w')
            pickle.dump(self.common.dontgivepkgs, file)
            file.close()
        except IOError, e:
            if e.errno == 13:
                self.logger.warn("Package synchro state serialization, serialize failed permission denied while accessing file %s"%(self.filename))
                return False
            elif e.errno == 2:
                self.logger.warn("Package synchro state serialization, serialize failed, no such file or directory %s"%(self.filename))
                return False
            self.logger.warn("Package synchro state serialization, serialize failed accessing file: %s"%(str(e)))
            return False
        except Exception, e:
            self.logger.debug("Package synchro state serialization, serialize failed: %s"%(str(e)))
            return False
        self.logger.debug("Package synchro state serialization, serialize succeed")
        return True

    def unserialize(self):
        self.logger.debug("Package synchro state serialization, unserialize")
        # will unserialize file into self.common.dontgivepkgs
        try:
            if not os.path.exists(self.filename):
                return False
            file = open(self.filename, 'r')
            r = pickle.load(file)
            file.close()
            if type(r) == dict:
                self.common.dontgivepkgs = r
                self.logger.debug("Package synchro state serialization, unserialize succeed")
                return True
            self.logger.debug("Package synchro state serialization, unserialize failed")
            return False
        except IOError, e:
            if e.errno == 13:
                self.logger.warn("Package synchro state serialization, unserialize failed permission denied while accessing file %s"%(self.filename))
                return False
            elif e.errno == 2:
                self.logger.warn("Package synchro state serialization, unserialize failed, no such file or directory %s"%(self.filename))
                return False
            self.logger.warn("Package synchro state serialization, unserialize failed accessing file: %s"%(str(e)))
            return False
        except Exception, e:
            self.logger.debug("Package synchro state serialization, unserialize failed: %s"%(str(e)))
            return False


