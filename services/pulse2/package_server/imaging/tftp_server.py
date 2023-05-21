#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
A TFTP server to serve dynamically generated bootmenus

"""


# Twisted stuff for tftp server
from pulse2.package_server.imaging.api.functions import Imaging
from ptftplib.tftpserver import TFTPServer, TFTPServerConfigurationError
from twisted.internet.threads import deferToThread
import logging
from time import time
import twisted
from twisted.python import threadable

threadable.init(1)
thread = deferToThread.__get__  # Create an alias for deferred functions


class StringFileHandler:
    data = ""

    def __init__(self, data):
        self.data = data

    def close(self):
        pass

    def flush(self):
        pass

    def read(self, a):
        if len(self.data) <= a:
            output = self.data
            self.data = ""
        else:
            output = self.data[0:a]
            self.data = self.data[a:]
        return output


class ImagingTFTPServer(object):
    iface = "eth0"
    root = "/var/lib/pulse2/imaging"
    port = 69
    strict_rfc1350 = False
    server = None
    file_cache = {}
    running = False

    def __init__(self):
        # TODO: read config and set params
        self.logger = logging.getLogger()

        def file_handler(TFTPServerHandler, path):
            # Function that handles virtual files serving
            # Example path: /var/lib/pulse2/imaging/bootmenus/0800275532AF
            try:
                if path in self.file_cache and self.file_cache[path][0] - time() < 10:
                    data = self.file_cache[path][1]
                else:
                    if "bootmenus/" in path:
                        # Serving a computer bootmenu
                        x = path.split("bootmenus/")[1]
                        # Get computer mac from path
                        mac = ":".join([x[2 * i] + x[2 * i + 1] for i in range(6)])

                        data = Imaging().getBuiltMenu(mac)
                    self.file_cache[path] = [int(time()), data]
                    self.logger.error(data)
            except BaseException:
                # Serve the default bootmenu
                data = ""

            data = data
            self.logger.error(data)
            _file = StringFileHandler(data)
            _filesize = len(data)

            return _file, _filesize

        # Set a signal catcher to get sigterm
        try:
            # Instanciate server object
            self.server = TFTPServer(
                self.iface,
                self.root,
                self.port,
                self.strict_rfc1350,
                dynamic_file_callback=file_handler,
            )
            # Add a signal catcher for SIGTERM
            twisted.internet.reactor.addSystemEventTrigger(
                "before", "shutdown", self.signal_handler
            )
        except Exception as e:
            self.logger.error(str(e))

    def signal_handler(self):
        try:
            if self.running:
                self.server.server.shutdown()
        except Exception as e:
            print(str(e))

    def listen(self):
        try:
            deferToThread(self.server.serve_forever)
            self.running = True
        except TFTPServerConfigurationError as e:
            self.logger.error("TFTP server configuration error: %s!" % e.message)
