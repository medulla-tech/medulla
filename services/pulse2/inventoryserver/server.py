# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
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

import BaseHTTPServer
from zlib import *
from time import strftime
import logging
import time
import re
import signal
import os
import sys
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from threading import Thread, Semaphore
import threading

from pulse2.database.inventory import InventoryCreator
from pulse2.database.inventory.mapping import OcsMapping
from pulse2.database.inventory.entitiesrules import EntitiesRules, DefaultEntityRules
from pulse2.utils import Singleton
from pulse2.inventoryserver.config import Pulse2OcsserverConfigParser
from pulse2.inventoryserver.ssl import *

class InventoryServer:
    def log_message(self, format, *args):
        self.logger.info(format % args)

    def do_POST(self):
        content = self.rfile.read(int(self.headers['Content-Length']))
        resp = ''

        # handle compressed inventories
        if self.headers['Content-Type'].lower() == 'application/x-compress':
            content = decompressobj().decompress(content)

        cont = [content, self.headers['Content-Type']]

        try:
            query = re.search(r'<QUERY>([\w-]+)</QUERY>', content).group(1)
        except AttributeError, e:
            query = 'FAILS'
        try:
            deviceid = re.search(r'<DEVICEID>([\w-]+)</DEVICEID>', content).group(1)
        except AttributeError, e:
            pass

        if query == 'PROLOG':
            config = InventoryGetService().config
            if len(config.options.keys()) == 0:
                resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>SEND</RESPONSE></REPLY>'
            else:
                resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY>'
                for section in config.options:
                    try:
                        params = config.options[section]
                        resp += '<OPTION><NAME>%s</NAME>' % (params['name'])
                        resp_param = ""
                        for p in params['param']:
                            resp_param += '<PARAM '
                            for attr in p['param']:
                                resp_param += '%s="%s" ' % (attr[0], attr[1])
                            resp_param += '>%s</PARAM>' % (p['value'])
                        resp += resp_param + '</OPTION>'
                    except:
                        self.logger.error('please check your %s config parameter' % (section))
                resp = resp + '<RESPONSE>SEND</RESPONSE></REPLY>'
        elif query == 'UPDATE':
            resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>no_update</RESPONSE></REPLY>'
        elif query == 'INVENTORY':
            resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>no_account_update</RESPONSE></REPLY>'
            Common().addInventory(deviceid, cont)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(compress(resp))

class HttpInventoryServer(BaseHTTPServer.BaseHTTPRequestHandler, InventoryServer):
    def __init__(self, *args):
        self.logger = logging.getLogger()
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)
    def log_message(self, format, *args):
        self.logger.info(format % args)

class HttpsInventoryServer(SecureHTTPRequestHandler, InventoryServer):
    def __init__(self, *args):
        self.logger = logging.getLogger()
        SecureHTTPRequestHandler.__init__(self, *args)
    def log_message(self, format, *args):
        self.logger.info(format % args)

class TreatInv(Thread):
    def __init__(self, config):
        Thread.__init__(self)
        self.status = -1
        self.logger = logging.getLogger()
        self.config = config

    def log_message(self, format, *args):
        self.logger.info(format % args)

    def run(self):
        while 1:
            while Common().countInventories() > 0:
                self.logger.debug("TreatInv :: there are %d inventories"%Common().countInventories())
                deviceid, content = Common().popInventory()
                if not self.treatinv(deviceid, content):
                    self.logger.debug("TreatInv :: failed to create inventory for device %s"%(deviceid))
            self.logger.debug("TreatInv :: there are no new inventories")
            time.sleep(15) # TODO put in the conf file

    def treatinv(self, deviceid, cont):
        content = cont[0]

        try:
            start_date = time.time()
            threadname = threading.currentThread().getName().split("-")[1]
            inv_data, encoding, date = '', '', strftime("%Y-%m-%d %H:%M:%S")
            self.logger.debug("Thread %s : starting process : %s " % (threadname, time.time()))
            try:
                inv_data = re.compile(r'<CONTENT>(.+)</CONTENT>', re.DOTALL).search(content).group(1)
            except AttributeError, e:
                pass

            try:
                encoding = re.search(r' encoding="([^"]+)"', content).group(1)
            except AttributeError, e:
                pass

            try:
                date = re.compile(r'<LOGDATE>(.+)</LOGDATE>', re.DOTALL).search(inv_data).group(1)
            except AttributeError, e:
                pass

            self.logger.debug("Thread %s : regex : %s " % (threadname, time.time()))
            inventory = '<?xml version="1.0" encoding="%s" ?><Inventory>%s</Inventory>' % (encoding, inv_data)
            inventory = re.sub(r'</?HISTORY>', '', inventory)
            inventory = re.sub(r'</?DOWNLOAD>', '', inventory)

            resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>no_account_update</RESPONSE></REPLY>'

            # Store data on the server
            inventory = OcsMapping().parse(inventory)
            self.logger.debug("Thread %s : parsed : %s " % (threadname, time.time()))
            hostname = '-'.join(deviceid.split('-')[0:-6])
            self.logger.debug("Thread %s : Original hostname : %s" % (threadname, hostname))
            try:
                path = Pulse2OcsserverConfigParser().hostname
                # WARNING : no fallback if the tag does not exists....
                if len(path) == 3:
                    if path[0] in inventory:
                        found_tag = False
                        for tag in inventory[path[0]]:
                            self.logger.debug("tag = %s" % tag)
                            if path[2][0] in tag and tag[path[2][0]] == path[2][1]:
                                found_tag = True
                                hostname = tag[path[1]]
                        if not found_tag:
                            self.logger.warn("Thread %s : Can't alter hostname for %s using tag: tag %s was not found in %s" % (threadname, hostname, path[2][1], tag))
                    else:
                        self.logger.warn("Thread %s : Can't find %s in inventory to alter hostname for %s" % (threadname, path[0], hostname))

                    self.logger.debug("Thread %s : Final hostname, 3 components path: %s" % (threadname, hostname))
                else:
                    hostname = inventory[path[0]][0][path[1]]
                    self.logger.debug("Thread %s : Final hostname, 2 components path: %s" % (threadname, hostname))
            except Exception, e:
                self.logger.exception(e)
                self.logger.error("inventory = %s" % inventory)
            try:
                date = inventory['ACCESSLOG'][1]['LOGDATE']
            except:
                pass

            # Assign an entity to the computer
            entities = InventoryCreator().rules.compute(inventory)
            if entities:
                entity = entities[0]
            else:
                entity = InventoryCreator().config.default_entity
            inventory['Entity'] = [ { 'Label' : entity } ]

            self.logger.debug("Thread %s : prepared : %s " % (threadname, time.time()))
            ret = InventoryCreator().createNewInventory(hostname, inventory, date)
            self.logger.debug("Thread %s : done : %s " % (threadname, time.time()))
            # TODO if ret == False : reply something else
            end_date = time.time()

            self.logger.info("Injected inventory for %s in %s seconds" % (hostname, end_date - start_date))

            if not ret:
                self.logger.error("no inventory created!")
                return False

        except IOError, e:
            self.logger.exception(e)
            self.logger.error(e.orig)
        except Exception, e:
            self.logger.exception(e)

        return True

class Common(Singleton):
    inventories = []
    sem = Semaphore()
    shutdownRequest = False

    def addInventory(self, deviceId, content):
        self.sem.acquire()
        self.inventories.append([deviceId, content])
        self.sem.release()

    def countInventories(self):
        self.sem.acquire()
        count = len(self.inventories)
        self.sem.release()
        return count

    def popInventory(self):
        self.sem.acquire()
        deviceId, content = self.inventories.pop()
        self.sem.release()
        return (deviceId, content)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class InventoryGetService(Singleton):
    def initialise(self, config):
        self.logger = logging.getLogger()
        self.xmlmapping = config.ocsmapping
        try:
            OcsMapping().initialize(self.xmlmapping)
        except IOError, e:
            self.logger.error(e)
            return False
        try:
            InventoryCreator().activate(config)
        except Exception, e :
            self.logger.error(e)
            return False
        if not InventoryCreator().db_check():
            return False
        self.config = config
        # Initialize the computer to entity mapping
        if self.config.entities_rules_file:
            try:
                InventoryCreator().rules = EntitiesRules(self.config.entities_rules_file)
            except Exception, e:
                self.logger.error(e)
                return False
        else:
            InventoryCreator().rules = DefaultEntityRules(self.config.default_entity)
        # Check that the default assigned entity exists
        if not InventoryCreator().locationExists(self.config.default_entity):
            self.logger.error("Default entity '%s' does not exist in database" % self.config.default_entity)
            return False
        self.bind = config.bind
        self.port = int(config.port)
        return True

    def run(self, server_class=ThreadedHTTPServer, handler_class=HttpInventoryServer): # by default launch a multithreaded server without ssl
        # Install SIGTERM handler
        signal.signal(signal.SIGTERM, self.handler)
        signal.signal(signal.SIGINT, self.handler)

        self.logger.debug("Start launching of treat inventory thread")
        self.treatinv = TreatInv(self.config)
        self.treatinv.setDaemon(True)
        self.treatinv.start()
        self.logger.debug("Treat inventory thread started")

        server_address = (self.bind, int(self.port))
        if self.config.enablessl: # warning if ssl is activated, given server and handler class will be override...
            self.logger.info("Starting server in ssl mode")
            handler_class = HttpsInventoryServer
            server_class = SecureThreadedHTTPServer
            self.httpd = server_class(server_address, handler_class, self.config)
        else:
            server_class = HTTPServer
            self.httpd = server_class(server_address, handler_class)
        if hasattr(self.httpd, 'daemon_threads'):
            self.httpd.daemon_threads = True
        self.httpd.serve_forever()

    def handler(self, signum, frame):
        """
        SIGTERM handler
        """
        self.logger.info("Shutting down...")
        os.seteuid(0)
        os.setegid(0)
        try:
            os.unlink(self.config.pidfile)
        except OSError:
            pass

        sys.exit(0)
