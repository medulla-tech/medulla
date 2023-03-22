# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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
        # imaging.synchroComputer args are (uuid, mac, wol)
        args = [uuid, False, wol]

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
