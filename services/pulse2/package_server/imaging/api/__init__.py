#!/usr/bin/python
# -*- coding: utf-8; -*-
#
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

"""
    Pulse2 PackageServer Mirror API
"""
import logging
from pulse2.package_server.imaging.common import ImagingCommon
from pulse2.package_server.xmlrpc import MyXmlrpc

class ImagingApi(MyXmlrpc):
    type = 'Imaging'
    def __init__(self, mp, src):
        MyXmlrpc.__init__(self)
        self.logger = logging.getLogger()
        self.src = src
            
        self.mp = mp
        self.logger.info("(%s) %s : initialised (%s)"%(self.type, self.mp, self.src))

    def xmlrpc_getServerDetails(self):
        pass
