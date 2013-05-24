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

"""
Inventory server http server part.
"""

import BaseHTTPServer
from zlib import decompressobj, compress
from time import strftime
import logging
import time
import re
import signal
import os
import sys
import imp
import traceback
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from threading import Thread, Semaphore
import threading

from pulse2.database.inventory import InventoryCreator, Inventory
from pulse2.database.inventory.mapping import OcsMapping
from pulse2.database.inventory.entitiesrules import EntitiesRules, DefaultEntityRules
from pulse2.utils import Singleton
from mmc.site import mmcconfdir
from pulse2.inventoryserver.config import Pulse2OcsserverConfigParser
from pulse2.inventoryserver.ssl import SecureHTTPRequestHandler, SecureThreadedHTTPServer
from pulse2.inventoryserver.utils import InventoryUtils
from pulse2.inventoryserver.scheduler import AttemptToScheduler
from pulse2.inventoryserver.glpiproxy import GlpiProxy, resolveGlpiMachineUUIDByMAC


class InventoryServer:
    def log_message(self, format, *args):
        self.logger.info(format % args)

    def do_GET(self):
        self.logger.debug("GET http method - ignore")

    def do_POST(self):
        content = self.rfile.read(int(self.headers['Content-Length']))
        resp = ''
        from_ip = self.client_address[0]
        deviceid = ''

        # handle compressed inventories
        # application/x-compress is for OCS
        # application/x-compress is for Fusion
        if self.headers['Content-Type'].lower() in ['application/x-compress', 'application/x-compress-zlib']:
            try:
                decomp = decompressobj()
                content = decomp.decompress(content)
                if decomp.unused_data:
                    self.logger.warn("The content of the request from %s seems to be bad."%(from_ip))
                    self.logger.debug("The remaining bytes are : %s"%(decomp.unused_data))
            except Exception, e:
                self.logger.error("Failed while decompressing the request from %s."%(from_ip))
                self.logger.error(str(e))

        cont = [content, self.headers['Content-Type']]

        # Forwarding the inventories to GLPI
        if self.config.enable_forward :
            self.glpi_forward(content, from_ip)

        try:
            query = re.search(r'<QUERY>([\w-]+)</QUERY>', content).group(1)
        except AttributeError, e:
            self.logger.warn("Could not get any QUERY section in inventory from %s"%(from_ip))
            query = 'FAILS'
        try:
            if query != 'UPDATE':
                deviceid = re.search(r'<DEVICEID>([\w.-]+)</DEVICEID>', content).group(1)
        except AttributeError, e:
            self.logger.warn("Could not get any DEVICEID section in inventory from %s"%(from_ip))
            self.logger.debug("no DEVICEID in %s"%(content))
            query = 'FAILS'

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
            self.logger.debug("Inventory update from %s" % from_ip)
            resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>no_update</RESPONSE></REPLY>'
        elif query == 'INVENTORY':
            self.logger.debug("New inventory from %s" % from_ip)
            resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>no_account_update</RESPONSE></REPLY>'
            Common().addInventory(deviceid, from_ip, cont)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(compress(resp))

    def glpi_forward(self, content, from_ip):
        """
        Some checks and controls before the forwarding the invontory to GLPI

        @param content: invntory on XML format
        @type content: str

        @param from_ip: IP address of machine which is sending the inventory
        @type from_ip: str
        """
        try:

            macaddresses = InventoryUtils.getMACs(content)
            self.logger.debug("GlpiProxy: MAC addresses found: %s" % str(macaddresses))
            if len(macaddresses) > 0 :
                glpi_uuid = None
                for macaddr in macaddresses :
                    self.logger.debug("GlpiProxy: Trying to resolve a machine with MAC address=%s" % macaddr)
                    glpi_uuid = resolveGlpiMachineUUIDByMAC(macaddr)
                    if glpi_uuid :
                        self.logger.debug("GlpiProxy: Resolved machine UUID='%s'" % str(glpi_uuid))
                        break
                if not (glpi_uuid and InventoryUtils.is_comming_from_pxe(from_ip)) :  
                    glpi_proxy = GlpiProxy(self.config.url_to_forward)
                    self.logger.info("GlpiProxy: Forwarding the inventory to GLPI")

                    # Let's fix the XML using py config scripts
                    invfix = InventoryFix(self.config, content)
                    content = invfix.get()

                    glpi_proxy.send(content)
                    for msg in glpi_proxy.result :
                        self.logger.warn("GlpiProxy: %s" % msg)
                else :
                    self.logger.info("GlpiProxy: Incoming from PXE, ignoring the forward for a existing machine")
            else :
                self.logger.debug("GlpiProxy: New machine inscription or forwarding the prolog")
                glpi_proxy = GlpiProxy(self.config.url_to_forward)
                invfix = InventoryFix(self.config, content)
                content = invfix.get()

                glpi_proxy.send(content)
                for msg in glpi_proxy.result :
                    self.logger.warn("GlpiProxy: %s" % msg)

        except Exception, e :
            self.logger.error("GlpiProxy: %s" % str(e))


class InventoryFix :
    """Let's fix the XML using py config scripts"""

    def __init__(self, config, inventory):
        self.config = config
        self._inventory = inventory
        self.logger = logging.getLogger()
        self.logger.debug("Initialize the inventory fixer")

        self.fixers = []
        self._check_in()
        self._update()
 
    def _check_in (self):
       """ 
       Find and pre-check all .py from xmlfixplugindir.
       Checked module must have a calable function named 'xml_fix'.       
       """
       for (path, dirs, files) in os.walk(self.config.xmlfixplugindir):
          for filename in files:
              pathname = os.path.join(path, filename)
              if re.match('^.*\.py$',pathname):
                  mod_name = filename 
                  py_mod = fnc = None
                  try:
                      py_mod = imp.load_source(mod_name, pathname)
                      
                  except ImportError :
                      self.logger.warn("Cannot load fixing script '%s'" % filename)
                      continue
                  except Exception, e :
                      self.logger.warn("Unable to run %s script: %s" % (filename, e))
                      continue

                  if hasattr(py_mod, 'xml_fix'):
                      fnc = getattr(py_mod, 'xml_fix')
                      if hasattr(fnc, "__call__") :
                          self.fixers.append(fnc)
                      else :
                          self.logger.warn("module %s : attribute xml_fix is not a function or method" %  filename)
                  else :
                      self.logger.warn("Unable to run %s script: missing xml_fix() function" % filename)
                                      
 
    def _update (self):
        """Aply the script on inventory"""
        for fnc in self.fixers :
            try :
                self._inventory = fnc(self._inventory)
                self.logger.info("Inventory fixed by '%s' script" % fnc.__module__)
            except :
                info = sys.exc_info()
                for fname, linenumber, fnc_name, text in traceback.extract_tb(info[2]):
                    args = (fname, linenumber, fnc_name)
                    self.logger.error("module: %s line: %d in function: %s" % args)
                    self.logger.error("Failed on: %s" % text)

    def get (self):
        """get the fixed inventory"""
        return self._inventory



class HttpInventoryServer(BaseHTTPServer.BaseHTTPRequestHandler, InventoryServer):
    def __init__(self, *args):
        self.logger = logging.getLogger()
        cfgfile = os.path.join(mmcconfdir,"pulse2","inventory-server","inventory-server.ini")
        self.config = Pulse2OcsserverConfigParser()
        self.config.setup(cfgfile)
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)
    def log_message(self, format, *args):
        self.logger.info(format % args)

class HttpsInventoryServer(SecureHTTPRequestHandler, InventoryServer):
    def __init__(self, *args):
        self.logger = logging.getLogger()
        cfgfile = os.path.join(mmcconfdir,"pulse2","inventory-server","inventory-server.ini")
        self.config = Pulse2OcsserverConfigParser()
        self.config.setup(cfgfile)
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
                deviceid, from_ip, content = Common().popInventory()
                if not self.treatinv(deviceid, from_ip, content):
                    self.logger.debug("TreatInv :: failed to create inventory for device %s"%(deviceid))
            self.logger.debug("TreatInv :: there are no new inventories")
            time.sleep(15) # TODO put in the conf file

    def treatinv(self, deviceid, from_ip, cont):
        content = cont[0]
        self.logger.debug('### BEGIN INVENTORY')
        self.logger.debug('%s' % cont)
        self.logger.debug('### END INVENTORY')
        macaddresses = InventoryUtils.getMACs(content)
        self.logger.debug("MAC addresses found: %s" % str(macaddresses))
        final_macaddr = None

        setLastFlag = True

        # GLPI case - inventory creating disabled 
        if self.config.enable_forward and len(macaddresses) > 0:
            try :
                for macaddr in macaddresses :
                    self.logger.debug("Trying to resolve a machine with MAC address=%s" % macaddr)
                    glpi_machine_uuid = resolveGlpiMachineUUIDByMAC(macaddr) 
                    if glpi_machine_uuid :
                        self.logger.debug("Resolved machine UUID='%s'" % str(glpi_machine_uuid))
                        AttemptToScheduler(from_ip, glpi_machine_uuid)
                        final_macaddr = macaddr
                        break
                    else :
                        self.logger.warn("GLPI machine couldn't be resolved, skipping the light pull.")
            except Exception, exc :
                self.logger.error("GLPI light pull mode: %s" % str(exc))
        if self.config.disable_create_inventory :
            self.logger.debug("Access to database disabled - exit the inventory creator")
            return False

        if InventoryUtils.is_comming_from_pxe(from_ip):
            self.logger.debug("Inventory is coming from PXE")
            inv = Inventory()
            inv.activate(self.config)
            setLastFlag = not inv.isInventoried(final_macaddr)

        try:
            start_date = time.time()
            threadname = threading.currentThread().getName().split("-")[1]
            inv_data, encoding, date = '', '', strftime("%Y-%m-%d %H:%M:%S")
            current_entity = ''

            self.logger.debug("Thread %s : starting process : %s " % (threadname, time.time()))
            try:
                inv_data = re.compile(r'<CONTENT>(.+)</CONTENT>', re.DOTALL).search(content).group(1)
            except AttributeError, e:
                # we can not work without it!
                self.logger.warn("Could not get any CONTENT section in inventory from %s"%(from_ip))
                self.logger.error("no inventory created!")
                return False

            try:
                encoding = re.search(r' encoding=["\']([^"\']+)["\']', content).group(1)
            except AttributeError, e:
                self.logger.warn("Could not get any encoding in inventory from %s"%(from_ip))

            try:
                date = re.compile(r'<LOGDATE>(.+)</LOGDATE>', re.DOTALL).search(inv_data).group(1)
            except AttributeError, e:
                # we can work without it
                self.logger.warn("Could not get any LOGDATE section in inventory from %s"%(from_ip))

            try:
                current_entity = re.compile(r'<TAG>(.+)</TAG>', re.DOTALL).search(content).group(1)
            except AttributeError, e:
                # we can work without it
                self.logger.warn("Could not get any TAG section in inventory from %s" % from_ip)

            self.logger.debug("Thread %s : regex : %s " % (threadname, time.time()))
            inventory = '<?xml version="1.0" encoding="%s" ?><Inventory>%s</Inventory>' % (encoding, inv_data)
            inventory = re.sub(r'</?HISTORY>', '', inventory)
            inventory = re.sub(r'</?DOWNLOAD>', '', inventory)

            # Let's fix the XML using py config scripts
            invfix = InventoryFix(self.config, inventory)
            inventory = invfix.get()
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
                            if path[2][0] in tag and tag[path[2][0]] == path[2][1] and path[1] in tag:
                                found_tag = True
                                hostname = tag[path[1]]
                        if not found_tag:
                            self.logger.warn("Thread %s : Can't alter hostname for %s using tag: tag value for %s/%s when %s/%s == %s not found" % (threadname, hostname, path[0], path[1], path[0], path[2][0], path[2][1]))
                    else:
                        self.logger.warn("Thread %s : Can't find %s in inventory to alter hostname for %s" % (threadname, path[0], hostname))

                    self.logger.debug("Thread %s : Final hostname, 3 components path: %s" % (threadname, hostname))
                else:
                    hostname = inventory[path[0]][0][path[1]]
                    self.logger.debug("Thread %s : Final hostname, 2 components path: %s" % (threadname, hostname))
            except Exception, e:
                self.logger.exception(e)
                self.logger.error("inventory = %s" % inventory)

            # Assign an entity to the computer
            entities = InventoryCreator().rules.compute(inventory)
            if entities:
                entity = entities[0]
            else:
                entity = InventoryCreator().config.default_entity

            # If no rule, use the entity in TAG
            if entity == InventoryCreator().config.default_entity and current_entity:
                entity = current_entity

            self.logger.debug("Computer '%s' assigned to entity '%s'" % (hostname, entity))
            inventory['Entity'] = [{'Label' : entity}]

            self.logger.debug("Thread %s : prepared : %s " % (threadname, time.time()))
            result = InventoryCreator().createNewInventory(hostname, inventory, date, setLastFlag)
            self.logger.debug("Thread %s : done : %s " % (threadname, time.time()))
            # TODO if ret == False : reply something else
            end_date = time.time()

            self.logger.info("Injected inventory for %s in %s seconds" % (hostname, end_date - start_date))

            ret = None
            if isinstance(result, list) and len(result) == 2 :
                # disabling light pull on GLPI mode when Pulse2 inventory creator is enabled
                if not self.config.enable_forward :
                    ret, machine_uuid = result
                    AttemptToScheduler(from_ip, machine_uuid)
            else :
                ret = result

            if not ret:
                self.logger.error("no inventory created!")
                return False

        except IOError, e:
            self.logger.exception(e)
            if hasattr(e, 'message') and e.message != '':
                self.logger.error(e.mesage)
        except Exception, e:
            self.logger.exception(e)

        return True

class Common(Singleton):
    inventories = []
    sem = Semaphore()
    shutdownRequest = False

    def addInventory(self, deviceId, from_ip, content):
        self.sem.acquire()
        self.inventories.append([deviceId, from_ip, content])
        self.sem.release()

    def countInventories(self):
        self.sem.acquire()
        count = len(self.inventories)
        self.sem.release()
        return count

    def popInventory(self):
        self.sem.acquire()
        deviceId, from_ip, content = self.inventories.pop()
        self.sem.release()
        return (deviceId, from_ip, content)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class InventoryGetService(Singleton):
    def initialise(self, config):
        self.logger = logging.getLogger()
        self.xmlmapping = config.ocsmapping
        self.bind = config.bind
        self.port = int(config.port)
        self.config = config

        try:
            OcsMapping().initialize(self.xmlmapping)
        except IOError, e:
            self.logger.error(e)
            return False
        if self.config.disable_create_inventory :
            return True

        try:
            if not InventoryCreator().activate(config): # does the db_check
                return False
        except Exception, e : # TODO improve to get the "not the good version" message
            self.logger.error(e)
            return False

        # Translate the default entity to its real name if the dot character
        # has been used in the configuration file
        if self.config.default_entity == '.':
            rootEntity = InventoryCreator().getRootLocation()
            self.config.default_entity = rootEntity.Label
        # Check that the default assigned entity exists
        if not InventoryCreator().locationExists(self.config.default_entity):
            self.logger.warning("Default entity '%s' does not exist in database" % self.config.default_entity)
            self.logger.warning("Creating entity '%s' in database" % self.config.default_entity)
            try:
                InventoryCreator().createEntity(self.config.default_entity)
            except Exception, e:
                self.logger.error("Can't create entity '%s'" % self.config.default_entity)
                self.logger.error(e)
                return False

        # Initialize the computer to entity mapping
        if self.config.entities_rules_file:
            try:
                InventoryCreator().rules = EntitiesRules(self.config.entities_rules_file)
            except Exception, e:
                self.logger.error(e)
                return False
        else:
            InventoryCreator().rules = DefaultEntityRules(self.config.default_entity)

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
            self.logger.warn("Couldn't unlink pid file %s"%(self.config.pidfile))

        sys.exit(0)

# patch BaseHTTPRequestHandler to handle nmap requests
def my_handle_one_request(self):
    try:
        return self.__handle_one_request()
    except Exception, e:
        if e.args[0] == 104 and e.args[1] == 'Connection reset by peer': # most probably is a nmap request
            logging.getLogger().info("nmap detected")
            return
        else:
            raise e

setattr(BaseHTTPRequestHandler, '__handle_one_request', BaseHTTPRequestHandler.handle_one_request)
setattr(BaseHTTPRequestHandler, 'handle_one_request', my_handle_one_request)

