#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2012 Mandriva, http://www.mandriva.com/
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

""" Common inventory utils """

import os
import logging 

from socket import gethostbyname
from xml.dom.minidom import parseString
from configobj import ConfigObj

from mmc.client.sync import Proxy
from mmc.site import mmcconfdir


class ConfigReader :
    """Read and parse config files"""
    def __init__(self):
        self._base_ini = os.path.join(mmcconfdir, 
                                "plugins", 
                                "base.ini")
        self._pkg_server_ini = os.path.join(mmcconfdir, 
                                      "pulse2",  
                                      "package-server", 
                                      "package-server.ini")
        self._img_server_ini = os.path.join(mmcconfdir, 
                                      "pulse2",  
                                      "imaging-server", 
                                      "imaging-server.ini")
        

    @classmethod
    def get_config(cls, inifile):
        """ 
        Get the configuration from config file
        
        @param inifile: path to config file
        @type inifile: string
    
        @return: ConfigParser.ConfigParser instance 
        """
        logging.getLogger().debug("<scheduler> : Load config file %s" % inifile)
        if not os.path.exists(inifile) :

            logging.getLogger().warn("Error while reading the config file:")
            logging.getLogger().warn("Not found.")

            raise IOError, "Config file '%s' not found" % inifile

        return ConfigObj(inifile)
 
    @property
    def img_server_config (self):
        """ 
        Get the configuration of imaging server 
             
        @return: ConfigParser.ConfigParser instance 
        """
        return self.get_config(self._img_server_ini)

    @property
    def pkg_server_config (self):
        """ 
        Get the configuration of package server 
             
        @return: ConfigParser.ConfigParser instance 
        """
        return self.get_config(self._pkg_server_ini)


    @property
    def base_config(self):
        """ 
        Get the configuration from base.ini
    
        @return: ConfigParser.ConfigParser instance 
        """
        return self.get_config(self._base_ini)


class MMCProxy :
    """ Provider to connect at mmc-agent """
    def __init__(self): 

        config = ConfigReader()
        
        self.pkg_server_config = config.pkg_server_config
        self.base_config = config.base_config
        
        self._failure = False

        self._url = None
        self._proxy = None

        self._build_url()

        if not self._failure :
            password = self._get_ldap_password()

        if not self._failure :
            self._build_proxy(password)

    def _build_url(self):
        """ URL building for XML-RPC proxy """
       
        if not "mmc_agent" in self.pkg_server_config :
            logging.getLogger().warn("Error while reading the config file:")
            logging.getLogger().warn("Section 'mmc_agent' not exists")
            self._failure = True
            return

        mmc_section =  self.pkg_server_config["mmc_agent"]

        for option in ["username", "password", "host", "port"] :

            if option not in mmc_section :
                logging.getLogger().warn("Error while reading section 'mmc_agent':")
                logging.getLogger().warn("Option '%s' not exists" % option)

                self._failure = True
                return
 
        username = mmc_section["username"]
        host = mmc_section["host"]
        password = mmc_section["password"]
        port = mmc_section["port"]
        
        logging.getLogger().debug("Building the connection URL at mmc-agent") 

        self._url = 'https://%s:%s@%s:%s' % (username, password, host, port)

    @property
    def failure (self):
        """ 
        Failure flag to indicate the incorrect build of proxy 

        @returns: bool
        """
        return self._failure

    def _get_ldap_password(self):
        """ 
        Password for LDAP authentification 
        
        @return: string
        """
       
        if not "ldap" in self.base_config :

            logging.getLogger().warn("Error while reading the config file: Section 'ldap'")

            self._failure = True
            return
                                
        return self.base_config["ldap"]["password"]

    def _build_proxy (self, password):
        """ Builds the XML-RPC proxy to MMC agent. """
        try :
            self._proxy = Proxy(self._url)

            logging.getLogger().debug("LDAP authentification")

            self._proxy.base.ldapAuth('root', password)

            logging.getLogger().debug("Create a mmc-agent proxy") 

        except Exception, err :
            logging.getLogger().error("Error while connecting to mmc-agent : %s" % err)
            self._failure = True
            

    @property
    def proxy (self):
        """
        Get the XML-RPC proxy to MMC agent.
        
        @return: mmc.client.sync.Proxy
        """
        return self._proxy
 


class InventoryUtils :
    """ Common inventory utils """


    @classmethod
    def get_pkg_server_ip(cls):
        """ 
        Get the ip address of package server. 
        
        @return: string
        """
        config = ConfigReader().img_server_config

        if "package-server" in config :
            if "host" in config["package-server"] :

                host = config["package-server"]["host"]
                return gethostbyname(host)

        return "127.0.0.1"

    @classmethod
    def is_comming_from_pxe(cls, from_ip):
        """ 
        Check if the inventory is coming from PXE.

        @param from_ip: IP address of inventory source 
        @type from_ip: string

        @return: bool
        """
        return from_ip == cls.get_pkg_server_ip()

    @classmethod
    def getMACs(cls, content):
        """
        Getting the MAC addresses from inventory XML

        @param content: incoming inventory in XML format
        @type content: str

        @return: list of MAC addresses
        @rtype: generator
        """
        dom = parseString(content)
        tags = dom.getElementsByTagName('MACADDR')

        macs = []

        if isinstance(tags, list) and len(tags) > 0:
            for tag in tags :
                xml_tag = tag.toxml()
                mac = xml_tag.replace('<MACADDR>','').replace('</MACADDR>','')
                macs.append(mac)

        return macs

