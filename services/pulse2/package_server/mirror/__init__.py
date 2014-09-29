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
    Pulse2 PackageServer Mirror API
"""
import logging
from pulse2.package_server.common import Common
from pulse2.package_server.xmlrpc import MyXmlrpc

class Mirror(MyXmlrpc):
    type = 'Mirror'
    def __init__(self, mp, name = ''):
        MyXmlrpc.__init__(self)
        self.logger = logging.getLogger()
        self.name = name
        self.mp = mp
        if Common().getPackages(self.mp) == None:
            e = "(%s) %s : can't initialise at %s correctly"%(self.type, self.name, self.mp)
            self.logger.error(e)
            raise Exception(e)
        self.logger.info("(%s) %s : initialised with packages : %s"%(self.type, self.name, str(Common().getPackages(self.mp).keys())))

    def xmlrpc_getServerDetails(self):
        return map(lambda x: Common().package(x).toH(), Common().getPackages(self.mp))

    def xmlrpc_isAvailable(self, pid):
        return Common().getPackages(self.mp).has_key(pid)

    def xmlrpc_getFilesURI(self, fids):
        ret = []
        for fid in fids:
            ret.append(self.xmlrpc_getFilePath(fid))
        return ret

    def xmlrpc_getFileURI(self, fid):
        return self.xmlrpc_getFilePath(fid)

    def xmlrpc_getFilePath(self, fid):
        f = Common().getFile(fid, self.mp)
        if f == None:
            return ''
        else:
            return f

