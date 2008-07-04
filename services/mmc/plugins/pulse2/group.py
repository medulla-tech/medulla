#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
#
# This file is part of MMC.
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
from mmc.support.mmctools import Singleton

class ComputerGroupManager(Singleton):
    components = {}
    main = 'dyngroup'

    def __init__(self):
        Singleton.__init__(self)
        self.logger = logging.getLogger()

    def select(self, name):
        self.logger.info("Selecting computer group manager: %s" % name)
        self.main = name

    def register(self, name, klass):
        self.logger.debug("Registering computer group manager %s / %s" % (name, str(klass)))
        self.components[name] = klass

    def validate(self):
        return True

    def isdyn_group(self, ctx, gid):
        klass = self.components[self.main]
        return klass().isdyn_group(ctx, gid)

    def isrequest_group(self, ctx, gid):
        klass = self.components[self.main]
        return klass().isrequest_group(ctx, gid)

    def requestresult_group(self, ctx, gid, min, max, filter):
        klass = self.components[self.main]
        return klass().requestresult_group(ctx, gid, min, max, filter)

    def result_group(self, ctx, gid, min, max, filter):
        klass = self.components[self.main]
        return klass().result_group(ctx, gid, min, max, filter)

    def request(self, ctx, query, bool, min, max, filter):
        klass = self.components[self.main]
        return klass().request(ctx, query, bool, min, max, filter)

class ComputerGroupI:
    def isdyn_group(self, ctx, gid):
        """
        Says if the group is a dynamic group or not (return a bool)
        """
        pass

    def isrequest_group(self, ctx, gid):
        """
        Says if the dynamic group is a request or a result (return a bool)
        """
        pass

    def requestresult_group(self, ctx, gid, min, max, filter):
        """
        Reply to this group query and send the result
        """
        pass

    def result_group(self, ctx, gid, min, max, filter):
        """
        Send the group content
        """
        pass

    def request(self, ctx, query, bool, min, max, filter):
        """
        Reply to this query
        """
        return []


