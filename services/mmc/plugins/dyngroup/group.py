#
# (c) 2008 Mandriva, http://www.mandriva.com/
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

from pulse2.managers.group import ComputerGroupI
from mmc.plugins.dyngroup.database import DyngroupDatabase
from mmc.plugins.dyngroup.qmanager import QueryManager

class DyngroupGroup(ComputerGroupI):

    def isdyn_group(self, ctx, gid):
        """
        Says if the group is a dynamic group or not (return a bool)
        """
        return DyngroupDatabase().isdyn_group(ctx, gid)

    def isrequest_group(self, ctx, gid):
        """
        Says if the dynamic group is a request or a result (return a bool)
        """
        return DyngroupDatabase().isrequest_group(ctx, gid)

    def requestresult_group(self, ctx, gid, min, max, filter):
        """
        Reply to this group query and send the result
        """
        return DyngroupDatabase().requestresult_group(ctx, gid, min, max, filter, QueryManager())

    def result_group(self, ctx, gid, min, max, filter, idOnly = True):
        """
        Send the group content
        """
        return DyngroupDatabase().result_group(ctx, gid, min, max, filter, idOnly)

    def countresult_group(self, ctx, gid, filter):
        """
        Count the group content
        """
        return DyngroupDatabase().countresult_group(ctx, gid, filter)

    def request(self, ctx, query, bool, min, max, filter):
        """
        Reply to this query
        """
        return DyngroupDatabase().request(ctx, query, bool, min, max, filter, QueryManager())

    def result_group_by_name(self, ctx, name, min, max, filter):
        """
        Send the group content, given a group name
        """
        return DyngroupDatabase().result_group_by_name(ctx, name, min, max, filter, QueryManager())


