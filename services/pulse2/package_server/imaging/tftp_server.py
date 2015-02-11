#!/usr/bin/python
# -*- coding: utf-8; -*-
"""
"""
#
# (c) 2013 Mandriva, http://www.mandriva.com/
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
A TFTP server to serve dynamically generated bootmenus

"""

import logging
from time import time
import twisted

# Twisted stuff for tftp server
from twisted.python import threadable; threadable.init(1)
from twisted.internet.threads import deferToThread
thread = deferToThread.__get__ #Create an alias for deferred functions

from ptftplib.tftpserver import TFTPServer, TFTPServerConfigurationError
from pulse2.package_server.imaging.api.functions import Imaging

class StringFileHandler:

    data = ''

    def __init__(self, data):
        self.data = data

    def close(self):
        pass

    def flush(self):
        pass

    def read(self, a):
        if len(self.data) <= a:
            output = self.data
            self.data = ''
        else:
            output = self.data[0:a]
            self.data = self.data[a:]
        return output



class ImagingTFTPServer(object):
    iface = 'eth0'
    root = '/var/lib/pulse2/imaging'
    port = 69
    strict_rfc1350 = False
    server = None
    file_cache = {}
    running = False

    def __init__(self):
        # TODO: read config and set params
        self.logger = logging.getLogger()

        def file_handler(TFTPServerHandler, path):
            # Function that handles virtual files serving
            # Example path: /var/lib/pulse2/imaging/bootmenus/0800275532AF
            try:
                if path in self.file_cache and self.file_cache[path][0] - time() < 10:
                    data = self.file_cache[path][1]
                else:
                    if 'bootmenus/' in path:
                        # Serving a computer bootmenu
                        x = path.split('bootmenus/')[1]
                        # Get computer mac from path
                        mac = ':'.join([x[2*i]+x[2*i+1] for i in xrange(6)])

                        data = Imaging().getBuiltMenu(mac)
                    self.file_cache[path] = [int(time()), data]
                    self.logger.error(data)
            except:
                # Serve the default bootmenu
                data = ''

            data = data
            self.logger.error(data)
            _file = StringFileHandler(data)
            _filesize = len(data)

            return _file, _filesize

        # Set a signal catcher to get sigterm
        try:
            # Instanciate server object
            self.server = TFTPServer(self.iface,
                    self.root,
                    self.port,
                    self.strict_rfc1350,
                    dynamic_file_callback=file_handler
                    )
            # Add a signal catcher for SIGTERM
            twisted.internet.reactor.addSystemEventTrigger('before', 'shutdown', self.signal_handler)
        except Exception, e:
            self.logger.error(str(e))


    def signal_handler(self):
        try:
            if self.running:
                self.server.server.shutdown()
        except Exception, e:
            print str(e)

    def listen(self):
        try:
            deferToThread(self.server.serve_forever)
            self.running = True
        except TFTPServerConfigurationError, e:
            self.logger.error('TFTP server configuration error: %s!' %
                          e.message)
