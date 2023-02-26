# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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
        if os.path.isfile(inifile + '.local'):
            config.readfp(open(inifile + '.local','r'))

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

        log.debug("Execute remote function %s" % (fnc))
        return d.callRemote(fnc, *args, **kwargs)
