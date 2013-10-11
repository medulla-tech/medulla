# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
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

import os
import logging

from mmc.site import mmcconfdir
from ConfigParser import ConfigParser
from mmc.client.async import Proxy

log = logging.getLogger()

class ConfigReader(object):
    """Read and parse config files"""
    def __init__(self):
        scheduler_ini = os.path.join(mmcconfdir, 
                                      "pulse2",  
                                      "scheduler", 
                                      "scheduler.ini")

        self._scheduler_config = self.get_config(scheduler_ini)


    @classmethod
    def get_config(cls, inifile):
        """
        Get the configuration from config file

        @param inifile: path to config file
        @type inifile: string

        @return: ConfigParser.ConfigParser instance 
        """
        log.debug("Load config file %s" % inifile)
        if not os.path.exists(inifile) :
            logging.getLogger().error("Error while reading the config file: Not found.")
            return False

        config = ConfigParser()
        config.readfp(open(inifile))

        return config

    @property
    def scheduler_config(self):
        """ 
        Get the configuration of package server 

        @return: ConfigParser.ConfigParser instance 
        """
        return self._scheduler_config

class MMCProxy(object):
    """ Provider to connect at mmc-agent """
    def __init__(self): 

        config = ConfigReader()

        self.scheduler_config = config.scheduler_config

        self._url = None
        self._proxy = None

        self._username = self.scheduler_config.get("mmc_agent", "username")
        self._password = self.scheduler_config.get("mmc_agent", "password")
        self._build_url()

    def _build_url(self):
        """ URL building for XML-RPC proxy """

        if not self.scheduler_config.has_section("mmc_agent") :
            log.error("Error while reading the config file: Section 'mmc_agent' not exists")
            return False

        host = self.scheduler_config.get("mmc_agent", "host")
        port = self.scheduler_config.get("mmc_agent", "port")

        log.debug("Building the connection URL at mmc-agent") 
        self._url = 'https://%s:%s/XMLRPC' % (host, port)

    def _build_proxy(self):
        """ Builds the XML-RPC proxy to MMC agent. """
        log.debug("Building mmc-agent proxy")

        try:
            return Proxy(self._url, self._username, self._password)

        except Exception, err:
            log.error("Error while connecting to mmc-agent : %s" % err)
            return False


    def proxy (self):
        """
        Get the XML-RPC proxy to MMC agent.

        @return: mmc.client.sync.Proxy
        """
        return self._build_proxy()

class RPCClient(MMCProxy) :
    """ 
    XML-RPC Handler to execute remote functions. 
    """

    def rpc_execute(self, fnc, *args, **kwargs):
        """ 
        Remote execution handler

        @param fnc: RPC function to call
        @type fnc: function type  

        @param args: Arguments of called function
        @type args: *args type (list) 

        @param kwargs: Arguments of called function
        @type kwargs: **kwargs type (dict) 
        """

        d = self.proxy()

        log.error("Execute remote function %s" % (fnc))
        return d.callRemote(fnc, *args, **kwargs)
