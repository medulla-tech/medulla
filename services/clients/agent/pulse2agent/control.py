# -*- test-case-name: pulse2.msc.client.tests.control -*-
# -*- coding: utf-8; -*-
#
# (c) 2014 Mandriva, http://www.mandriva.com/
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

import os
import sys
import stat
import time
import logging
import logging.config
import platform
import urllib2
import fileinput

from distutils import file_util

from ptypes import CC
from ptypes import  Component, DispatcherFrame
from connect import ClientEndpoint
from connect import ConnectionTimeout, ConnectionRefused
from inventory import InventoryChecker, get_minimal_inventory
from vpn import VPNLaunchControl
from shell import Shell
from pexceptions import SoftwareCheckError, ConnectionError
from pexceptions import SoftwareInstallError, PackageDownloadError



class Protocol(Component):
    # TODO - generalize and sychronize with server side
    __component_name__ = "protocol"

    def get_command(self, cmd):
        if cmd == "GET":
            return "packages.get_package"
        elif cmd == "TICK":
            return "scheduler.tick"
        elif cmd == "INVENTORY":
            return "inventory.process_inventory"
        elif cmd == "VPN_SET":
            return "vpn_install.create_new_user"



class InventorySender(Component):
    __component_name__ = "inventory_sender"

    def send(self):
        inventory = get_minimal_inventory()
        command = self.parent.protocol.get_command("INVENTORY")

        container = (command, inventory)
        try:
            response = self.parent.client.request(container)
            self.logger.debug("inventory: received response: %s" % response)
        except ConnectionError:
            return False
        return True

class VPNSetter(Component):
    __component_name__ = "vpn_setter"

    def _create_user_on_server(self):
        inventory = get_minimal_inventory()
        command = self.parent.protocol.get_command("VPN_SET")

        container = (command, inventory)
        return self.parent.client.request(container)

    def create_user_on_server(self):
        response = self._create_user_on_server()
        self.logger.debug("vpn_setter: received response: %s" % response)
        try:
            if isinstance(response, list):
                if len(response) == 4:
                    host, port, user, password = response
                    ok = self.set_variables(host, port, user, password)
                    if ok:
                        self.logger.debug("vpn_setter: variables successfully assigned")
                        return self.install()

                    return True
        except Exception, e:
            self.logger.warn("VPN install failed: %s" % str(e))

        return False

    def get_created_connection(self):

        response = self._create_user_on_server()
        self.logger.debug("vpn_setter: received response: %s" % response)
        try:
            if isinstance(response, list):
                if len(response) == 4:
                    host, port, user, password = response
                    return "/VPN_SERVER=%s /VPN_PORT=%s /VPN_LOGIN=%s /VPN_PASSWORD=%s" % (host, port, user, password)

            raise SoftwareInstallError("vpnclient")
        except ValueError:
            raise SoftwareInstallError("vpnclient")



    def set_variables(self, host, port, user, password):
        variables = os.path.join(self.temp_dir,
                                 "vpn-variables",
                                 )
        file_util.copy_file("%s.in" % variables, variables)
        pattern = {"VPN_SERVER_HOST": host,
                   "VPN_SERVER_PORT": port,
                   "VPN_SERVER_USER": user,
                   "VPN_SERVER_PASSWORD": password,
                   "VPN_SERVICE_SIDE": "client",
                   }
        return self.replace(pattern, variables)


    def replace(self, pattern, in_script):
        """
        Replaces all occurences based on pattern.

        @param pattern: key as template expression, value as new string
        @type pattern: dict

        @return: True if all occurences replaced
        @rtype: bool
        """
        replaced_items = 0
        for line in fileinput.input(in_script, inplace=1):
            for (old, new) in pattern.iteritems():
                search_exp = "@@%s@@" % old
                if search_exp in line:
                    line = line.replace(search_exp, new)
                    replaced_items += 1
            sys.stdout.write(line)

        return replaced_items == len(pattern)


    def install(self):
        installer = os.path.join(self.temp_dir,
                                 "vpn-service-install.sh",
                                 )
        self.logger.debug("vpn_setter: chmod +x installer")
        st = os.stat(installer)
        os.chmod(installer, st.st_mode | stat.S_IEXEC)

        exitcode = self.parent.shell.call(installer)
        if exitcode != 0:
            self.logger.warn("vpn_setter: install failed")
            return False

        setter = os.path.join(self.temp_dir,
                              "vpn-client-set.sh",
                              )
        st = os.stat(setter)
        os.chmod(setter, st.st_mode | stat.S_IEXEC)
        self.logger.debug("vpn_setter: chmod +x setter")

        exitcode = self.parent.shell.call(setter)
        if exitcode != 0:
            self.logger.warn("vpn_setter: set failed")
            return False


        return True

    @property
    def temp_dir(self):
        if platform.system() == "Windows":
           return self.config.paths.package_tmp_dir_win
        else:
           return self.config.paths.package_tmp_dir_posix




class InitialInstalls(Component):
    """Provides a simple downloader with following install etap"""

    __component_name__ = "initial_installs"

    def install(self, software, *args):
        """
        Gets the requested from server and installs it.

        @param software: name of software
        @type software: str

        @return: True if download and install was successfull
        @rtype: bool
        """
        command = self.parent.protocol.get_command("GET")

        request = {"name": software,
                   "system": platform.system(),
                   "arch": platform.machine(),
                   }
        if platform.system() == "Linux":
            request["distro"] = platform.linux_distribution()[0]
            request["xserver"] = 1 if "DISPLAY" in os.environ else 0


        container = (command, request)

        commands = self.parent.client.request(container)
        self.logger.debug("received response: %s" % commands)

        for command in commands:
            self.logger.info("execute command: %s" % command)
            self.do_cmd(command, *args)

        # TODO - include a delete phase



    def do_cmd(self, command, *args):
        if "##server##" in command:
            command = command.replace("##server##",
                                      "http://%s" % self.config.vpn.host)
        if "##wget##" in command:
            url = command.replace("##wget##","")
            self.logger.debug("dwnld url: %s" % url)
            self.download(url)
            return
        if "##args##" in command:
            command = command.replace("##args##", " ".join(args)).strip()

        if "##tmp##" in command:

            command = command.replace("##tmp##", "").strip()
            command = os.path.join(self.temp_dir, command)
            self.logger.debug("execute command in temp: %s" % command)
            self.launch(command)
        else:
            self.launch(command)

    @property
    def temp_dir(self):
        if platform.system() == "Windows":
           return self.config.paths.package_tmp_dir_win
        else:
           return self.config.paths.package_tmp_dir_posix


    def download(self, url):
        filename = url.split('/')[-1]
        try:
            u = urllib2.urlopen(url)
        except urllib2.URLError:
            self.logger.error("Unable to open URL: %s" % url)
            raise PackageDownloadError(url)
        self.logger.debug("start download from url: %s" % url)

        if not os.path.exists(self.temp_dir):
            os.mkdir(self.temp_dir)

        path = os.path.join(self.temp_dir, filename)
        f = open(path, 'wb')
        meta = u.info()
        filesize = int(meta.getheaders("Content-Length")[0])
        self.logger.debug("Downloading: %s bytes: %s" % (filename, filesize))

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)

        f.close()
        return path




    def unpack_to_tempfile(self, name, response):
        # TODO - distinct several serialisation backends
        import pickle

        path = os.path.join(self.config.paths.packages_temp_dir, name)
        f = open(name, "wb")

        pickle.dump(response, f)

        f.close()

        if os.path.exists(path):
            return path
        else:
            raise # something


    def launch(self, path):

        returncode = self.parent.shell.call(path)
        return True if returncode == 0 else False




class FirstRunEtap(Component):

    __component_name__ = "first_run_etap"

    def check_required(self):
        vpn_installed = False
        try:
            missing_software = self.parent.inventory_checker.check_missing()
        except SoftwareCheckError:
            self.logger.warn("Unable to continue, exit from first run step")
            return False

        except Exception, e:
            self.logger.warn("Unable to continue, another reason: %s" % str(e))
            return False

        if self.config.vpn.enabled:
            self.logger.debug("check if VPN installed...")
            if not self.parent.inventory_checker.check_vpn_installed():
                self.logger.debug("adding the vpnclient to required sw (missing=%s)" % repr(missing_software))
                #missing_software.append("vpnclient")
                vpn_installed = False
            else:
                vpn_installed = True


        try:
            for sw in missing_software:
                result = self.parent.initial_installs.install(sw)
                if not result:
                    pass
                    #raise SoftwareRequestError(sw)

            if self.config.vpn.enabled and not vpn_installed:

                if platform.system() == "Windows":
                    if self.config.vpn.common_connection_for_all:
                        result = self.parent.initial_installs.install(["vpnclient"])
                    else:
                        args = self.parent.vpn_setter.get_created_connection()
                        self.logger.debug("created args: %s" % str(args))
                        result = self.parent.initial_installs.install(["vpnclient"], args)

                        self.logger.debug("install of vpnclient: %s" % str(result))

                    self.logger.debug("install of vpnclient: %s" % str(result))
                else:
                    result = self.parent.initial_installs.install(["vpnclient"])
                    self.logger.debug("install of vpnclient: %s" % str(result))
                    result = self.parent.vpn_setter.create_user_on_server()
                    self.logger.debug("create_user_on_server: %s" % str(result))
        except PackageDownloadError:
            self.logger.warn("Initial install phase failed")
            return False
        except SoftwareInstallError, e:
            self.logger.warn("Install of %s failed (probably machine not exist yet in inventory" % str(e))
            return False
        return True






class Dispatcher(DispatcherFrame):

    components = [Shell,
                  FirstRunEtap,
                  InitialInstalls,
                  InventoryChecker,
                  InventorySender,
                  VPNLaunchControl,
                  VPNSetter,
                  Protocol,
                  ]

    def __init__(self, config):
        """
        @param config: config container
        @type config: Config

        @param vpn_queue: queue to collect results from forked process
        @type vpn_queue: Queue.Queue
        """
        super(self.__class__, self).__init__(config)


    def _connect(self):
        """
        The client connection build.

        @return: True if connection was successfully
        @rtype: bool
        """

        try:
            self.client = ClientEndpoint(self.config)
            time.sleep(2)
            self.client.connect()
            time.sleep(2)

            self.logger.debug("CLIENT: %s" % repr(self.client.socket))
            if not self.client.socket:
                self.logger.warn("Unable to build a connection to server")
                return False
            else:
                self.logger.info("Client successfully connected to server")
                return True

        except ConnectionRefused, exc:
            self.logger.error("Agent connection failed: %s" % repr(exc))
            return False

        except ConnectionTimeout, exc:
            self.logger.error("Agent connection failed: %s" % repr(exc))
            return False

        except Exception, exc:
            self.logger.error("Agent connection failed: %s" % repr(exc))
            return False



    def start(self):
        if not self.config.vpn.enabled:
            # VPN connection not included, if server not available, exit
            return self._connect()
        else:
            if not self._connect():
                # server not available, try to establish a VPN connection
                #launch_vpn = VPNLaunchControl(self.config, self.queues.vpn)
                if not self.inventory_checker.check_vpn_installed():
                    self.logger.warn("VPN client not installed yet")
                    return False
                ret = self.vpn_launch_control.start()
                if ret == CC.VPN | CC.DONE:
                    # VPN established, try to contact the server
                    time.sleep(self.config.vpn.startup_delay)
                    return self._connect()
                elif ret == CC.VPN | CC.FAILED:
                    # Unable to start VPN -> exit
                    self.logger.error("VPN client launching failed")
                    return False
                else:
                    self.logger.error("VPN client launching failed, another error")
            else:
                # first step succeed (direct connect without VPN)
                return True


    def _mainloop(self):
        # connection establishing
        if not self.start():
            # TODO - stop queues, log something and exit
            return False

        if not self.first_run_etap.check_required():
            # TODO - stop queues, log something and exit
            return False


        if not self.inventory_sender.send():
            return False
        # looking for all needed softwares and install them if missing


        while True:
            self.logger.debug("waiting for next period")
            time.sleep(self.config.main.check_period)
            if not self.inventory_sender.send():
                return False

    def mainloop(self):
        while True:
            self._mainloop()
            self.logger.info("Try to reconnect...")
            time.sleep(self.config.main.check_period)


def start():
    from config import Config

    cfgfile = os.path.join("/", "etc", "pulse2agent.ini")
    config = Config()
    config.read(cfgfile)
    logging.config.fileConfig(cfgfile)

    d = Dispatcher(config)
    d.mainloop()

if __name__ == "__main__":
    start()
