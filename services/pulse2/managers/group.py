# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
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

import logging
from pulse2.utils import Singleton

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

    def result_group(self, ctx, gid, min, max, filter, idOnly = True):
        klass = self.components[self.main]
        return klass().result_group(ctx, gid, min, max, filter, idOnly)

    def countresult_group(self, ctx, gid, filter):
        klass = self.components[self.main]
        return klass().countresult_group(ctx, gid, filter)

    def get_group_results(self, ctx, gid, min, max, filter, idOnly = True):
        """
        Wrapper that according to the group type calls result_group (static
        or stored results for a group) or requestresult_group (dynamic group)
        """
        if self.isdyn_group(ctx, gid):
            if self.isrequest_group(ctx, gid):
                ret = self.requestresult_group(ctx, gid, min, max, filter)
            else:
                ret = self.result_group(ctx, gid, min, max, filter, True)
        else:
            ret = self.result_group(ctx, gid, min, max, filter, True)
        return ret
            
    def request(self, ctx, query, bool, min, max, filter):
        klass = self.components[self.main]
        return klass().request(ctx, query, bool, min, max, filter)

    def result_group_by_name(self, ctx, name, min = 0, max = -1, filter = ''):
        klass = self.components[self.main]
        return klass().result_group_by_name(ctx, name, min, max, filter)

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

    def result_group(self, ctx, gid, min, max, filter, idOnly):
        """
        Send the group content
        """
        pass

    def request(self, ctx, query, bool, min, max, filter):
        """
        Reply to this query
        """
        return []

    def result_group_by_name(self, ctx, name, min, max, filter):
        """
        Send the group content, given a group name
        """
        pass

