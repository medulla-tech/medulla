import logging
from mmc.plugins.pulse2.group import ComputerGroupI
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
            

