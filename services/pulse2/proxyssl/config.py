#!/usr/bin/python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import re

from pulse2.proxyssl.utilities import Singleton
import ConfigParser
import sys


class Pulse2InventoryProxyConfig(Singleton):
    server = ''
    port = 9999
    local_port = 9999
    path = '/'
    command_name = "C:\Program Files\OCS Inventory Agent\OCSInventory.exe"
    command_attr = "/SERVER:127.0.0.1 /PNUM:9999"
    enablessl = True
    verifypeer = False
    key_file = "conf/key/privkey.pem"
    cert_file = "conf/key/cacert.pem"
    polling = False
    polling_time = 600
    flag = ('Software\\Mandriva\\Inventory\\Client', 'do_inventory')
    flag_type = 'reg'

    umask = ''
    daemon_group = 'root'
    daemon_user = 'root'

    improve = True
    savexmlModified = False
    updatedetection = False
    addicon = False

    getOcsDebugLog = False


    def setup(self, config_file = 'conf/p2ipc.ini'):
        # Load configuration file
        self.cp = ConfigParser.ConfigParser()
        self.cp.read(config_file)
        self.cp.read(config_file + '.local')
        self.logger = logging.getLogger()

        if self.cp.has_option('main', 'server'):
            self.server = self.cp.get('main', 'server')
        if self.cp.has_option('main', 'port'):
            self.port = self.cp.getint('main', 'port')
        if self.cp.has_option('main', 'local_port'):
            self.port = self.cp.getint('main', 'local_port')
        if self.cp.has_option('main', 'path'):
            self.path = self.cp.get('main', 'path')
        if self.cp.has_option('main', 'command_name'):
            self.command_name = self.cp.get('main', 'command_name')
        if self.cp.has_option('main', 'command_attr'):
            self.command_attr = self.cp.get('main', 'command_attr').split(' ')
        if self.cp.has_option('main', 'enablessl'):
            self.enablessl = self.cp.getboolean('main', 'enablessl')
        if self.cp.has_option('main', 'verifypeer'):
            self.verifypeer = self.cp.getboolean('main', 'verifypeer')
        if self.cp.has_option('main', 'localcert'):
            self.key_file= self.cp.get('main', 'localcert')
        if self.cp.has_option('main', 'cacert'):
            self.cert_file = self.cp.get('main', 'cacert')
        if self.cp.has_option('polling', 'activate') and self.cp.getboolean('polling', 'activate'):
            self.polling = True
            if self.cp.has_option('polling', 'type') and self.cp.get('polling', 'type') == 'reg':
                self.flag_type = 'reg'
            else:
                self.logger.error("don't know this type of polling flag")
                sys.exit(-1)
            if self.cp.has_option('polling', 'time'):
                self.polling_time = self.cp.getint('polling', 'time')
            if self.cp.has_option('polling', 'path'):
                # TODO if path is given with '/' convert, get the last part to put is as name, remove the begining is HKLM
                path = re.sub("/", "\\\\", self.cp.get('polling', 'path')).split('\\')
                flag = path.pop()
                if path[0] == 'HKEY_LOCAL_MACHINE':
                    path.reverse()
                    path.pop()
                    path.reverse()
                self.flag = ('\\'.join(path), flag)

        if self.cp.has_option('xmlupdate', 'enable'):
            self.improve = self.cp.getboolean('xmlupdate', 'enable')
        if self.cp.has_option('xmlupdate', 'keepxmlupdate'):
            self.savexmlmodified = self.cp.getboolean('xmlupdate', 'keepxmlupdate')
        if self.cp.has_option('xmlupdate', 'updatedetection'):
            self.updatedetection = self.cp.getboolean('xmlupdate', 'updatedetection')
        if self.cp.has_option('xmlupdate', 'addicon'):
            self.addicon = self.cp.getboolean('xmlupdate', 'addicon')

        if self.cp.has_option('ocsdebug', 'enable'):
             self.getocsdebuglog = self.cp.getboolean('ocsdebug', 'enable')
             if self.getocsdebuglog:
                 self.command_attr.append("/debug")
