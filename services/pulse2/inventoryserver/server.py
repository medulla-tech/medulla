# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Inventory server http server part.
"""

import http.server
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
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn, ForkingMixIn
from threading import Thread, Semaphore
import threading

from pulse2.database.inventory import InventoryCreator, Inventory
from pulse2.database.inventory.mapping import OcsMapping
from pulse2.database.inventory.entitiesrules import EntitiesRules, DefaultEntityRules
from pulse2.utils import Singleton
from mmc.site import mmcconfdir
from pulse2.inventoryserver.config import Pulse2OcsserverConfigParser
from pulse2.inventoryserver.ssl import (
    SecureHTTPRequestHandler,
    SecureThreadedHTTPServer,
)
from pulse2.inventoryserver.utils import InventoryUtils, canDoInventory
from pulse2.inventoryserver.scheduler import AttemptToScheduler
from pulse2.inventoryserver.glpiproxy import (
    GlpiProxy,
    resolveGlpiMachineUUIDByMAC,
    hasKnownOS,
)


def decosingleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class InventoryServer:
    def log_message(self, format, *args):
        self.logger.debug(format % args)

    def do_GET(self):
        from_ip = self.client_address[0]
        dest_path = self.path
        self.logger.debug(
            "HTTP GET request received for %s from %s" % (str(dest_path), str(from_ip))
        )
        if dest_path.startswith("/lpull?"):
            macs = dest_path.split("?")[1]
            macs = [x for x in macs.split("&") if x != ""]
            self.logger.debug("Light Pull requested for macs %s" % macs)
            AttemptToScheduler("<xml/>", resolveGlpiMachineUUIDByMAC(macs))
        self.send_response(200)

    def do_POST(self):
        content = self.rfile.read(int(self.headers["Content-Length"]))
        resp = ""
        from_ip = self.client_address[0]
        deviceid = ""

        # handle compressed inventories
        # application/x-compress is for OCS
        # application/x-compress is for Fusion
        if "compress" in self.headers["Content-Type"]:
            try:
                decomp = decompressobj()
                content = decomp.decompress(content)
                if decomp.unused_data:
                    self.logger.warn(
                        "The content of the request from %s seems to be bad."
                        % (from_ip)
                    )
                    self.logger.debug(
                        "The remaining bytes are : %s" % (decomp.unused_data)
                    )
            except Exception as e:
                self.logger.error(
                    "Failed while decompressing the request from %s." % (from_ip)
                )
                self.logger.error(str(e))

        cont = [content, self.headers["Content-Type"]]

        # Let's figure out a few things about this incoming XML...
        try:
            query = re.search(r"<QUERY>([\w-]+)</QUERY>", content).group(1)
        except AttributeError as e:
            self.logger.warn(
                "Could not get any QUERY section in inventory from %s" % from_ip
            )
            query = "FAILS"
        try:
            if query != "UPDATE":
                deviceid = re.search(
                    r"<DEVICEID>([\w.-]+)</DEVICEID>",
                    content.decode("utf8"),
                    re.UNICODE,
                ).group(1)
        except AttributeError as e:
            self.logger.warn(
                "Could not get any DEVICEID section in inventory from %s" % (from_ip)
            )
            self.logger.debug("no DEVICEID in %s" % (content))
            query = "FAILS"

        if query == "PROLOG":
            self.logger.info(
                "PROLOG received from %s (DEVICEID: %s)" % (from_ip, deviceid)
            )
            config = InventoryGetService().config
            resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY>'
            for section in config.options:
                try:
                    params = config.options[section]
                    resp += "<OPTION><NAME>%s</NAME>" % (params["name"])
                    resp_param = ""
                    for p in params["param"]:
                        resp_param += "<PARAM "
                        for attr in p["param"]:
                            resp_param += '%s="%s" ' % (attr[0], attr[1])
                        resp_param += ">%s</PARAM>" % (p["value"])
                    resp += resp_param + "</OPTION>"
                except BaseException:
                    self.logger.error(
                        "please check your %s config parameter" % (section)
                    )
            resp = resp + "<RESPONSE>SEND</RESPONSE>"
            self.logger.debug(
                "Inventory periodicity set to %s" % str(config.inventory_periodicity)
            )
            resp = (
                resp
                + "<PROLOG_FREQ>"
                + str(config.inventory_periodicity)
                + "</PROLOG_FREQ>"
            )
            resp = resp + "</REPLY>"
        elif query == "UPDATE":
            self.logger.info(
                "UPDATE received from %s (DEVICEID: %s)" % (from_ip, deviceid)
            )
            resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>no_update</RESPONSE></REPLY>'
        elif query == "INVENTORY":
            self.logger.info(
                "INVENTORY received from %s (DEVICEID: %s)" % (from_ip, deviceid)
            )
            resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>no_account_update</RESPONSE></REPLY>'
            Common().addInventory(deviceid, from_ip, cont)
        # Forwarding the inventories to GLPI (if enabled)
        if self.config.enable_forward or self.config.enable_forward_ocsserver:
            self.glpi_forward(content, from_ip, query)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(compress(resp))

    def glpi_forward(self, content, from_ip, query):
        """
        Some checks and controls before the forwarding the invontory to GLPI

        @param content: inventory in XML format
        @type content: str

        @param from_ip: IP address of machine which is sending the inventory
        @type from_ip: str

        @param query: query type (ie: PROLOG, INVENTORY...)
        @type query: str
        """
        try:
            # Light Pull mode and/or decide to forward or not if coming for PXE
            if query == "INVENTORY":
                has_known_os = False
                macaddresses = InventoryUtils.getMACs(content)
                # Honestly, 00:00:00:00:00:00 can't be a good mac, trust me I'm
                # an engineer
                macaddresses = [x for x in macaddresses if not x == "00:00:00:00:00:00"]
                self.logger.info(
                    "<GlpiProxy> MAC addresses found: %s" % ", ".join(macaddresses)
                )
                glpi_uuid = None

                for macaddr in macaddresses:
                    self.logger.info(
                        "<GlpiProxy> Trying to associate to an existing machine using MAC %s"
                        % macaddr
                    )
                    try:
                        glpi_uuid = resolveGlpiMachineUUIDByMAC(macaddr)
                    except Exception as e:
                        self.logger.error(
                            "<GlpiProxy> Unable to resolve incoming inventory UUID (check mmc-agent connectivity): error was: %s"
                            % str(e)
                        )
                    if glpi_uuid:
                        self.logger.debug(
                            "<GlpiProxy> Match found using %s! UUID: %s"
                            % (macaddr, str(glpi_uuid))
                        )
                        has_known_os = hasKnownOS(glpi_uuid)
                        break
                else:
                    self.logger.info(
                        "<GlpiProxy> Unable to resolve machine ID using MAC %s New machine?"
                        % ", ".join(macaddresses)
                    )

                do_forward = False
                # Machine found in database
                if glpi_uuid:
                    # Machine found in database with real OS
                    if has_known_os:
                        # Machine found in database with real OS and new
                        # inventory is PXE
                        if InventoryUtils.is_coming_from_pxe(content):
                            self.logger.info(
                                "<GlpiProxy> Machine %s received a new PXE inventory from %s: skipping (don't overwrite real inventory)"
                                % (str(glpi_uuid), str(from_ip))
                            )
                            do_forward = False
                        # Machine found in database with real OS and new
                        # inventory is real inventory
                        else:
                            self.logger.info(
                                "<GlpiProxy> Machine %s received a new inventory from %s: forwarding"
                                % (str(glpi_uuid), str(from_ip))
                            )
                            do_forward = True
                    # Machine found in database with PXE OS
                    else:
                        # Machine found in database with PXE OS and new
                        # inventory is PXE
                        if InventoryUtils.is_coming_from_pxe(content):
                            self.logger.info(
                                "<GlpiProxy> Machine %s received a new PXE inventory from %s: forwarding (overwrite PXE inventory)"
                                % (str(glpi_uuid), str(from_ip))
                            )
                            do_forward = True
                        # Machine found in database with PXE OS and new
                        # inventory real inventory
                        else:
                            self.logger.info(
                                "<GlpiProxy> Machine %s received a new inventory from %s: forwarding (overwrite PXE inventory)"
                                % (str(glpi_uuid), str(from_ip))
                            )
                            do_forward = True
                # Machine is not known, forward anyway
                else:
                    if canDoInventory():
                        if InventoryUtils.is_coming_from_pxe(content):
                            self.logger.info(
                                "<GlpiProxy> PXE inventory received from %s for an unknown machine: forwarding"
                                % str(from_ip)
                            )
                            do_forward = True
                        else:
                            self.logger.info(
                                "<GlpiProxy> Inventory received from %s for an unknown machine: forwarding"
                                % str(from_ip)
                            )
                            do_forward = True
                    else:
                        self.logger.info(
                            "<GlpiProxy> Cannot forward inventory (operation denied)"
                        )

                # Let's forward if needed
                if do_forward:
                    # Let's fix the XML using py config scripts
                    invfix = InventoryFix(self.config, content)
                    content = invfix.get()

                    # And forward
                    glpi_proxy = GlpiProxy(self.config.url_to_forward)
                    glpi_proxy.send(content)
                    for msg in glpi_proxy.result:
                        self.logger.debug("<GlpiProxy> %s" % msg)

            # Not an INVENTORY request, forwarding anyway
            else:
                self.logger.info(
                    "<GlpiProxy> Forwarding query %s from %s"
                    % (str(query), str(from_ip))
                )

                glpi_proxy = GlpiProxy(self.config.url_to_forward)
                glpi_proxy.send(content)
                for msg in glpi_proxy.result:
                    self.logger.debug("<GlpiProxy> %s" % msg)

        except Exception as e:
            self.logger.error("<GlpiProxy> %s" % str(e))


class InventoryFix:
    """Let's fix the XML using py config scripts"""

    def __init__(self, config, inventory):
        self.config = config
        self._inventory = inventory
        self.logger = logging.getLogger()
        self.logger.debug("Initialize the inventory fixer")

        self.fixers = []
        self._check_in()
        self._update()

    def _check_in(self):
        """
        Find and pre-check all .py from xmlfixplugindir.
        Checked module must have a calable function named 'xml_fix'.
        """
        for path, dirs, files in os.walk(self.config.xmlfixplugindir):
            for filename in sorted(files):
                pathname = os.path.join(path, filename)
                if re.match("^.*\\.py$", pathname):
                    mod_name = filename
                    py_mod = fnc = None
                    try:
                        py_mod = imp.load_source(mod_name, pathname)

                    except ImportError:
                        self.logger.warn("Cannot load fixing script '%s'" % filename)
                        continue
                    except Exception as e:
                        self.logger.warn("Unable to run %s script: %s" % (filename, e))
                        continue

                    if hasattr(py_mod, "xml_fix"):
                        fnc = getattr(py_mod, "xml_fix")
                        if hasattr(fnc, "__call__"):
                            self.fixers.append(fnc)
                        else:
                            self.logger.warn(
                                "module %s : attribute xml_fix is not a function or method"
                                % filename
                            )
                    else:
                        self.logger.warn(
                            "Unable to run %s script: missing xml_fix() function"
                            % filename
                        )

    def _update(self):
        """Aply the script on inventory"""
        # Logging pre-modified xml to temp file
        if int(self.config.xmldumpactive) == 1:
            dumpdir = self.config.xmldumpdir
            #
            timestamp = str(int(time.time()))
            f = open(dumpdir + "/inventorylog-pre-" + timestamp + ".xml", "w")
            f.write(self._inventory)
            f.close()
        #
        for fnc in self.fixers:
            try:
                self._inventory = fnc(self._inventory)
                self.logger.debug("Inventory fixed by '%s' script" % fnc.__module__)
            except BaseException:
                info = sys.exc_info()
                for fname, linenumber, fnc_name, text in traceback.extract_tb(info[2]):
                    args = (fname, linenumber, fnc_name)
                    self.logger.error("module: %s line: %d in function: %s" % args)
                    self.logger.error("Failed on: %s" % text)

        # Logging the post modified xml file
        if int(self.config.xmldumpactive) == 1:
            dumpdir = self.config.xmldumpdir
            f = open(dumpdir + "/inventorylog-post-" + timestamp + ".xml", "w")
            f.write(self._inventory)
            f.close()

    def get(self):
        """get the fixed inventory"""
        return self._inventory


class HttpInventoryServer(http.server.BaseHTTPRequestHandler, InventoryServer):
    def __init__(self, *args):
        self.logger = logging.getLogger()
        cfgfile = os.path.join(
            mmcconfdir, "pulse2", "inventory-server", "inventory-server.ini"
        )
        self.config = Pulse2OcsserverConfigParser()
        self.config.setup(cfgfile)
        http.server.BaseHTTPRequestHandler.__init__(self, *args)

    def log_message(self, format, *args):
        self.logger.debug(format % args)


class HttpsInventoryServer(SecureHTTPRequestHandler, InventoryServer):
    def __init__(self, *args):
        self.logger = logging.getLogger()
        cfgfile = os.path.join(
            mmcconfdir, "pulse2", "inventory-server", "inventory-server.ini"
        )
        self.config = Pulse2OcsserverConfigParser()
        self.config.setup(cfgfile)
        SecureHTTPRequestHandler.__init__(self, *args)

    def log_message(self, format, *args):
        self.logger.debug(format % args)


class TreatInv(Thread):
    def __init__(self, config):
        Thread.__init__(self)
        self.status = -1
        self.logger = logging.getLogger()
        self.config = config

    def log_message(self, format, *args):
        self.logger.debug(format % args)

    def run(self):
        while True:
            while Common().countInventories() > 0:
                self.logger.debug(
                    "TreatInv :: there are %d inventories" % Common().countInventories()
                )
                deviceid, from_ip, content = Common().popInventory()
                if not self.treatinv(deviceid, from_ip, content):
                    self.logger.debug(
                        "TreatInv :: failed to create inventory for device %s"
                        % (deviceid)
                    )
            self.logger.debug("TreatInv :: there are no new inventories")
            time.sleep(15)  # TODO put in the conf file

    def treatinv(self, deviceid, from_ip, cont):
        content = cont[0]
        self.logger.debug("### BEGIN INVENTORY")
        self.logger.debug("%s" % cont)
        self.logger.debug("### END INVENTORY")
        macaddresses = InventoryUtils.getMACs(content)
        # Honestly, 00:00:00:00:00:00 can't be a good mac, trust me I'm an
        # engineer
        macaddresses = [x for x in macaddresses if not x == "00:00:00:00:00:00"]
        self.logger.info("MAC addresses found: %s" % ", ".join(macaddresses))
        final_macaddr = None

        setLastFlag = True

        # GLPI case - inventory creating disabled
        if self.config.enable_forward and len(macaddresses) > 0:
            try:
                for macaddr in macaddresses:
                    self.logger.debug(
                        "LightPull: Trying to associate %s to an existing GLPI machine using MAC %s"
                        % (deviceid, macaddr)
                    )
                    glpi_machine_uuid = resolveGlpiMachineUUIDByMAC(macaddr)
                    if glpi_machine_uuid:
                        self.logger.debug(
                            "LightPull: Machine %s resolved as GLPI %s using MAC %s"
                            % (deviceid, str(glpi_machine_uuid), macaddr)
                        )
                        AttemptToScheduler(content, glpi_machine_uuid)
                        final_macaddr = macaddr
                        break
                else:
                    self.logger.info(
                        "LightPull: Unable to resolve %s from GLPI using MAC %s, new machine?"
                        % (deviceid, ", ".join(macaddresses))
                    )
            except Exception as exc:
                self.logger.error(
                    "LightPull: An error occurred when trying to resolve UUID from GLPI: %s"
                    % str(exc)
                )

        if self.config.enable_forward and not self.config.enable_forward_ocsserver:
            return False

        # Native case - inventory handling
        coming_from_pxe = False

        if InventoryUtils.is_coming_from_pxe(content):
            self.logger.debug("Inventory is coming from PXE")
            inv = Inventory()
            inv.activate(self.config)
            setLastFlag = not inv.isInventoried(final_macaddr)
            coming_from_pxe = True

        try:
            start_date = time.time()
            threadname = threading.currentThread().getName().split("-")[1]
            inv_data, encoding, date = "", "", strftime("%Y-%m-%d %H:%M:%S")
            current_entity = ""

            self.logger.debug(
                "Thread %s : starting process : %s " % (threadname, time.time())
            )
            try:
                inv_data = (
                    re.compile(r"<CONTENT>(.+)</CONTENT>", re.DOTALL)
                    .search(content)
                    .group(1)
                )
            except AttributeError as e:
                # we can not work without it!
                self.logger.warn(
                    "Could not get any CONTENT section in inventory from %s" % (from_ip)
                )
                return False

            try:
                encoding = re.search(r' encoding=["\']([^"\']+)["\']', content).group(1)
            except AttributeError as e:
                self.logger.warn(
                    "Could not get any encoding in inventory from %s" % (from_ip)
                )

            try:
                date = (
                    re.compile(r"<LOGDATE>(.+)</LOGDATE>", re.DOTALL)
                    .search(inv_data)
                    .group(1)
                )
            except AttributeError as e:
                # we can work without it
                self.logger.warn(
                    "Could not get any LOGDATE section in inventory from %s" % (from_ip)
                )

            try:
                current_entity = (
                    re.compile(r"<TAG>(.+)</TAG>", re.DOTALL).search(content).group(1)
                )
            except AttributeError as e:
                # we can work without it
                self.logger.debug(
                    "Could not get any TAG section in inventory from %s" % from_ip
                )

            self.logger.debug("Thread %s : regex : %s " % (threadname, time.time()))
            inventory = (
                '<?xml version="1.0" encoding="%s" ?><Inventory>%s</Inventory>'
                % (encoding, inv_data)
            )
            inventory = re.sub(r"</?HISTORY>", "", inventory)
            inventory = re.sub(r"</?DOWNLOAD>", "", inventory)

            # Let's fix the XML using py config scripts
            invfix = InventoryFix(self.config, inventory)
            inventory = invfix.get()
            # Store data on the server
            inventory = OcsMapping().parse(inventory)
            self.logger.debug("Thread %s : parsed : %s " % (threadname, time.time()))
            hostname = "-".join(deviceid.split("-")[0:-6])
            self.logger.debug(
                "Thread %s : Original hostname : %s" % (threadname, hostname)
            )
            try:
                path = Pulse2OcsserverConfigParser().hostname
                # WARNING : no fallback if the tag does not exists....
                if len(path) == 3:
                    if path[0] in inventory:
                        found_tag = False
                        for tag in inventory[path[0]]:
                            self.logger.debug("tag = %s" % tag)
                            if (
                                path[2][0] in tag
                                and tag[path[2][0]] == path[2][1]
                                and path[1] in tag
                            ):
                                found_tag = True
                                hostname = tag[path[1]]
                        if not found_tag:
                            self.logger.warn(
                                "Thread %s : Can't alter hostname for %s using tag: tag value for %s/%s when %s/%s == %s not found"
                                % (
                                    threadname,
                                    hostname,
                                    path[0],
                                    path[1],
                                    path[0],
                                    path[2][0],
                                    path[2][1],
                                )
                            )
                    else:
                        self.logger.warn(
                            "Thread %s : Can't find %s in inventory to alter hostname for %s"
                            % (threadname, path[0], hostname)
                        )

                    self.logger.debug(
                        "Thread %s : Final hostname, 3 components path: %s"
                        % (threadname, hostname)
                    )
                else:
                    hostname = inventory[path[0]][0][path[1]]
                    self.logger.debug(
                        "Thread %s : Final hostname, 2 components path: %s"
                        % (threadname, hostname)
                    )
            except Exception as e:
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

            self.logger.info("Computer %s assigned to entity %s" % (hostname, entity))
            inventory["Entity"] = [{"Label": entity}]

            self.logger.debug("Thread %s : prepared : %s " % (threadname, time.time()))
            result = InventoryCreator().createNewInventory(
                hostname,
                inventory,
                date,
                setLastFlag,
                coming_from_pxe=coming_from_pxe,
                from_ip=from_ip,
            )
            self.logger.debug("Thread %s : done : %s " % (threadname, time.time()))
            # TODO if ret == False : reply something else
            end_date = time.time()

            self.logger.info(
                "Injected inventory for %s in %s seconds"
                % (hostname, end_date - start_date)
            )

            ret = None
            if isinstance(result, list) and len(result) == 2:
                # disabling light pull on GLPI mode when Pulse2 inventory
                # creator is enabled
                if (
                    not self.config.enable_forward
                    or self.config.enable_forward_ocsserver
                ):
                    ret, machine_uuid = result
                    AttemptToScheduler(content, machine_uuid)
            else:
                ret = result

            if not ret:
                self.logger.error("no inventory created!")
                return False

        except IOError as e:
            self.logger.exception(e)
            if hasattr(e, "message") and e.message != "":
                self.logger.error(e.mesage)
        except Exception as e:
            self.logger.exception(e)

        return True


# Singleton


@decosingleton
class Common:
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


class ThreadedHTTPServerFork(ForkingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    request_queue_size = 10000
    max_children = 10000


class ThreadedHTTPServerThread(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    request_queue_size = 10000
    max_children = 10000


class InventoryGetService(Singleton):
    def initialise(self, config):
        self.logger = logging.getLogger()
        self.xmlmapping = config.ocsmapping
        self.bind = config.bind
        self.port = int(config.port)
        self.config = config
        try:
            OcsMapping().initialize(self.xmlmapping)
        except IOError as e:
            self.logger.error(e)
            return False
        if self.config.enable_forward and not self.config.enable_forward_ocsserver:
            return True

        try:
            if not InventoryCreator().activate(config):  # does the db_check
                return False
        except Exception as e:  # TODO improve to get the "not the good version" message
            self.logger.error(e)
            return False

        # Translate the default entity to its real name if the dot character
        # has been used in the configuration file
        if self.config.default_entity == ".":
            rootEntity = InventoryCreator().getRootLocation()
            self.config.default_entity = rootEntity.Label
        # Check that the default assigned entity exists
        if not InventoryCreator().locationExists(self.config.default_entity):
            self.logger.warning(
                "Default entity '%s' does not exist in database"
                % self.config.default_entity
            )
            self.logger.warning(
                "Creating entity '%s' in database" % self.config.default_entity
            )
            try:
                InventoryCreator().createEntity(self.config.default_entity)
            except Exception as e:
                self.logger.error(
                    "Can't create entity '%s'" % self.config.default_entity
                )
                self.logger.error(e)
                return False

        # Initialize the computer to entity mapping
        if self.config.entities_rules_file:
            try:
                InventoryCreator().rules = EntitiesRules(
                    self.config.entities_rules_file
                )
            except Exception as e:
                self.logger.error(e)
                return False
        else:
            InventoryCreator().rules = DefaultEntityRules(self.config.default_entity)

        return True

    # by default launch a multithreaded server without ssl
    def run(
        self, server_class=ThreadedHTTPServerThread, handler_class=HttpInventoryServer
    ):
        # Install SIGTERM handler
        signal.signal(signal.SIGTERM, self.handler)
        signal.signal(signal.SIGINT, self.handler)
        self.logger.debug("Start launching of treat inventory thread")
        self.treatinv = TreatInv(self.config)
        self.treatinv.setDaemon(True)
        self.treatinv.start()
        self.logger.debug("Treat inventory thread started")

        server_address = (self.bind, int(self.port))
        # warning if ssl is activated, given server and handler class will be
        # override...
        if self.config.enablessl:
            self.logger.info("Starting server in ssl mode")
            handler_class = HttpsInventoryServer
            server_class = SecureThreadedHTTPServer
            self.httpd = server_class(server_address, handler_class, self.config)
        else:
            if self.config.enable_forward and not self.config.enable_forward_ocsserver:
                server_class = ThreadedHTTPServerFork
            else:
                server_class = ThreadedHTTPServerThread
            self.httpd = server_class(server_address, handler_class)

        if hasattr(self.httpd, "daemon_threads"):
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
            self.logger.warn("Couldn't unlink pid file %s" % (self.config.pidfile))

        sys.exit(0)


# patch BaseHTTPRequestHandler to handle nmap requests


def my_handle_one_request(self):
    try:
        return self.__handle_one_request()
    except Exception as e:
        # most probably is a nmap request
        if e.args[0] == 104 and e.args[1] == "Connection reset by peer":
            logging.getLogger().info("nmap detected")
            return
        else:
            raise e


setattr(
    BaseHTTPRequestHandler,
    "__handle_one_request",
    BaseHTTPRequestHandler.handle_one_request,
)
setattr(BaseHTTPRequestHandler, "handle_one_request", my_handle_one_request)
