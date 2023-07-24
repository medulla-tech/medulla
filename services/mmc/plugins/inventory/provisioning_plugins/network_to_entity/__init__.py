# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
import logging

from mmc.site import mmcconfdir
from mmc.plugins.inventory.provisioning_plugins import PluginEntitiesI
from pulse2.database.inventory.entitiesrules import EntitiesRules


class PluginEntities(PluginEntitiesI):
    def __init__(self):
        self.logger = logging.getLogger()

    def get(self, authtoken):
        nr = NetworkRules(mmcconfdir + "/plugins/provisioning-inventory")
        self.logger.debug("HTTP headers contains:")
        self.logger.debug(authtoken.session.http_headers)
        ret = nr.compute(authtoken)
        return ret


class NetworkRules(EntitiesRules):
    def _getValues(self, input, parameter):
        """
        Return the value of the given parameter from input.
        In this implementation, we are only able to get value from the user
        session.
        """
        aliases = {"ip": "session.http_headers.x-browser-ip"}
        if parameter in aliases:
            parameter = aliases[parameter]
        ret = []
        if parameter.startswith("session.http_headers."):
            param = parameter.split(".")[2]
            if param in input.session.http_headers:
                ret = [input.session.http_headers[param]]
        return ret
