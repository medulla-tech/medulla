# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
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
from pulse2.scheduler.api.mmc_client import RPCClient

log = logging.getLogger()

class ImagingAPI(RPCClient):
    def synchroComputer(self, uuid, wol = False):
        def _callback(result):
            return True

        def _errBack(result):
            return False

        # Function to call
        fnc = "imaging.synchroComputer"
        args = [uuid, wol]

        d = self.rpc_execute(fnc, *args)
        d.addCallback(_callback)
        d.addErrback(_errBack)
        return d

    def setWOLMenu(self, uuid, name):
        log.info("Wake-on-lan received for client %s, creating WOL specific imaging boot menu" % name)
        return self.synchroComputer(uuid, wol = True)

    def unsetWOLMenu(self, uuid, name, status='done', message="maximum time reached"):
        log.info("Wake-on-lan %s for client %s (%s), restoring non-WOL imaging boot menu" % (status, name, message))
        return self.synchroComputer(uuid, wol = False)
