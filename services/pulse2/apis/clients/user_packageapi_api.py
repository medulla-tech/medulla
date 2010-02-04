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

"""
This module define the user package_api API
It provide methods to tell which package_api a user can use to modify packages.
"""

from pulse2.apis.clients import Pulse2Api
        
class UserPackageApiApi(Pulse2Api):
    def __init__(self, *attr):
        self.name = "UserPackageApiApi"
        Pulse2Api.__init__(self, *attr)

    def getUserPackageApi(self, user):
        if self.initialized_failed:
            return {}
        d = self.callRemote("getUserPackageApi", {"name":user, "uuid":user})
        d.addErrback(self.onError, "UserPackageApiApi:getUserPackageApi", {"name":user, "uuid":user}, [{'ERR':'PULSE2ERROR_GETUSERPACKAGEAPI', 'mirror':self.server_addr.replace(self.credentials, '')}])
        return d
