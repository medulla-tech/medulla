#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva
#
# $Id: __init__.py 86 2008-06-05 12:29:00Z oroussy $
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
import datetime
import time
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext

from mmc.plugins.msc.package_api import PackageA
from mmc.plugins.pkgs.package_put_api import PackagePutA
from mmc.plugins.pkgs.user_packageapi_api import UserPackageApiApi
from mmc.plugins.pkgs.config import PkgsConfig


VERSION = "2.0.0"
APIVERSION = "0:0:0"
REVISION = int("$Rev: 86 $".split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    logger = logging.getLogger()
    logger.debug("Pkgs is activating")
    config = PkgsConfig("pkgs")
    if config.disabled:
        logger.warning("Plugin pkgs: disabled by configuration.")
        return False
    return True

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s

class RpcProxy(RpcProxyI):
    def getPApiDetail(self, pp_api_id):
        upas = self.upaa_getUserPackageApi()
        for upa in upas:
            if upa['uuid'] == pp_api_id:
                return upa
        return False

    # PackagePutA
    def ppa_getPackageDetail(self, pp_api_id, pid):
        upas = self.upaa_getUserPackageApi()
        for upa in upas:
            if upa['uuid'] == pp_api_id:
                return PackageA(upa).getPackageDetail(pid)
        return False
    
    def ppa_putPackageDetail(self, pp_api_id, package):
        upas = self.upaa_getUserPackageApi()
        for upa in upas:
            if upa['uuid'] == pp_api_id:
                return PackagePutA(upa).putPackageDetail(package)
        logging.getLogger().warn("Failed to put package details on %s"%(pp_api_id))
        return False
        
    def ppa_dropPackage(self, pp_api_id, pid):
        upas = self.upaa_getUserPackageApi()
        for upa in upas:
            if upa['uuid'] == pp_api_id:
                return PackagePutA(upa).dropPackage(pid)
        return False

    # UserPackageApiApi
    def upaa_getUserPackageApi(self):
        ctx = self.currentContext
        return UserPackageApiApi().getUserPackageApi(ctx.userid)

