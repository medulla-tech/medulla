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
import mmc.plugins.pkgs.config
import pulse2.apis.clients.package_put_api

class PackagePutA(pulse2.apis.clients.package_put_api.PackagePutA):
    def __init__(self, server, port = None, mountpoint = None, proto = 'http', login = ''):
        self.logger = logging.getLogger()
        credits = ''
        if type(server) == dict:
            mountpoint = server['mountpoint']
            port = server['port']
            proto = server['protocol']
            bind = server['server']
            if server.has_key('username') and server.has_key('password') and server['username'] != '':
                login = "%s:%s@" % (server['username'], server['password'])
                credits = "%s:%s" % (server['username'], server['password'])

        self.server_addr = '%s://%s%s:%s%s' % (proto, login, bind, str(port), mountpoint)
        self.logger.debug('PackagePutA will connect to %s' % (self.server_addr))

        self.config = mmc.plugins.pkgs.PkgsConfig("pkgs")
        if self.config.upaa_verifypeer:
            pulse2.apis.clients.package_put_api.PackagePutA.__init__(self, credits, self.server_addr, self.config.upaa_verifypeer, self.config.upaa_cacert, self.config.upaa_localcert)
        else:
            pulse2.apis.clients.package_put_api.PackagePutA.__init__(self, credits, self.server_addr)

