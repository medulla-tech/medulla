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

import logging

from mmc.site import mmcconfdir
from mmc.plugins.inventory.provisioning_plugins import PluginEntitiesI
from pulse2.database.inventory.entitiesrules import EntitiesRules

class PluginEntities(PluginEntitiesI):

    def __init__(self):
        self.logger = logging.getLogger()

    def get(self, authtoken):
        nr = NetworkRules(mmcconfdir + '/plugins/provisioning-inventory')
        self.logger.debug('HTTP headers contains:')
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
        aliases = { 'ip' : 'session.http_headers.x-browser-ip' }
        if parameter in aliases:
            parameter = aliases[parameter]
        ret = []
        if parameter.startswith('session.http_headers.'):
            param = parameter.split('.')[2]
            if param in input.session.http_headers:
                ret = [input.session.http_headers[param]]
        return ret
