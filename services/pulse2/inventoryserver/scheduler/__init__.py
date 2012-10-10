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

"""
Anticipated executing of scheduled tasks on scheduler.
"""
import os
import sys
import logging 


from time import sleep
from socket import gethostbyname
from configobj import ConfigObj

from mmc.client.sync import Proxy
from mmc.site import mmcconfdir


class ConfigReader :
    """Read and parse config files"""
    def __init__(self):
        base_ini = os.path.join(mmcconfdir, 
                                "plugins", 
                                "base.ini")
        pkg_server_ini = os.path.join(mmcconfdir, 
                                      "pulse2",  
                                      "package-server", 
                                      "package-server.ini")
        img_server_ini = os.path.join(mmcconfdir, 
                                      "pulse2",  
                                      "imaging-server", 
                                      "imaging-server.ini")
        
        self._base_config = self.get_config(base_ini)
        self._pkg_server_config = self.get_config(pkg_server_ini)
        self._img_server_config = self.get_config(img_server_ini)
        

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
            logging.getLogger().error("<scheduler> : Error while reading the config file:")
            logging.getLogger().error("<scheduler> : Not found.")
            sys.exit(2)

        return ConfigObj(inifile)
 
    @property
    def img_server_config (self):
        """ 
        Get the configuration of imaging server 
             
        @return: ConfigParser.ConfigParser instance 
        """
        return self._img_server_config

    @property
    def pkg_server_config (self):
        """ 
        Get the configuration of package server 
             
        @return: ConfigParser.ConfigParser instance 
        """
        return self._pkg_server_config


    @property
    def base_config(self):
        """ 
        Get the configuration from base.ini
    
        @return: ConfigParser.ConfigParser instance 
        """
        return self._base_config


class MMCProxy :
    """ Provider to connect at mmc-agent """
    def __init__(self): 

        config = ConfigReader()
        
        self.pkg_server_config = config.pkg_server_config
        self.base_config = config.base_config
        
        self._url = None
        self._proxy = None

        self._build_url()
        self._build_proxy()

    def _build_url(self):
        """ URL building for XML-RPC proxy """
       
        if not "mmc_agent" in self.pkg_server_config :
            logging.getLogger().error("<scheduler> : Error while reading the config file:")
            logging.getLogger().error("<scheduler> : Section 'mmc_agent' not exists")
            sys.exit(2)

        mmc_section =  self.pkg_server_config["mmc_agent"]

        username = mmc_section["username"]
        host = mmc_section["host"]
        password = mmc_section["password"]
        port = mmc_section["port"]
        
        logging.getLogger().debug("<scheduler> : Building the connection URL at mmc-agent") 

        self._url = 'https://%s:%s@%s:%s' % (username, password, host, port)
        
    def _get_ldap_password(self):
        """ 
        Password for LDAP authentification 
        
        @return: string
        """
       
        if not "ldap" in self.base_config :
            logging.getLogger().error("<scheduler> : Error while reading the config file: Section 'ldap'")
            sys.exit(2)
                                
        return self.base_config["ldap"]["password"]

    def _build_proxy (self):
        """ Builds the XML-RPC proxy to MMC agent. """
        try :
            self._proxy = Proxy(self._url)

            logging.getLogger().debug("<scheduler> : LDAP authentification")

            self._proxy.base.ldapAuth('root', self._get_ldap_password())

            logging.getLogger().debug("<scheduler> : Create a mmc-agent proxy") 

        except Exception, err :
            logging.getLogger().error("<scheduler> : Error while connecting to mmc-agent : %s" % err)
            sys.exit(2)

    @property
    def proxy (self):
        """
        Get the XML-RPC proxy to MMC agent.
        
        @return: mmc.client.sync.Proxy
        """
        return self._proxy
 


class AttemptToScheduler :
    """
    Trigger to early executions of scheduled attempts.

    This engine is called when an inventory is received.
    """

    # First delay after the inventory reception
    # TODO - move the delays in a .ini file ?
    FIRST_DELAY = 60 
    BETWEEN_TASKS_DELAY = 1

    def __init__(self, from_ip, uuid):
        """
        @param from_ip: IP address of inventory source 
        @type from_ip: string

        @param uuid: Host UUID
        @type uuid: string

        """
        # Test to resolve the inventory source
  
        if not self.is_comming_from_pxe(from_ip) :

            logging.getLogger().info("<scheduler> : Start")
            self.uuid = uuid
            mmc = MMCProxy()
            self.proxy = mmc.proxy
            self.dispatch_msc()
            logging.getLogger().info("<scheduler> : Return to inventory")

        else :

            logging.getLogger().info("<scheduler> : Incomming from PXE : ignore")

    def get_pkg_server_ip(self):
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

    def is_comming_from_pxe(self, from_ip):
        """ 
        Check if the inventory is incomming from PXE.

        @param from_ip: IP address of inventory source 
        @type from_ip: string

        @return: bool
        """
        return from_ip == self.get_pkg_server_ip()


    def dispatch_msc (self):
        """ 
        Get a filtered list of scheduled tasks and executing each of them.
        """

        params = {"uuid" : self.uuid}
        try :
            result = self.proxy.msc.displayLogs(params)
        except Exception, err :

            logging.getLogger().error("<scheduler> : Error while executing 'msc.displayLogs'")
            logging.getLogger().error("<scheduler> : %s" % err)                        
            return False

        _size, _tasks = result

        unauthorised_states = ['failed',
                               'done',
                               'upload_in_progress',
                               'execution_in_progress',
                               'delete_in_progress',
                               'inventory_in_progress',
                               'reboot_in_progress',
                               'wol_in_progress',
                               'halt_in_progress',
                               ]
 
        # task queryset structure (single line):
        # commands__columns, id, current_state, command_on_host__columns

        # we need only ids (cohs) excluding unauthorised states
        tasks = [a[1] for a in _tasks if a[2] not in unauthorised_states]

        if len(tasks) == 0 :
            logging.getLogger().debug("<scheduler> : Nothing to execute :")
            logging.getLogger().debug("<scheduler> : Exit")
            return
        else :
            # execute all commands on host :
            total = len(tasks)
            logging.getLogger().info("<scheduler> : Total tasks to execute: %s" % str(total))

            success = self.start_all_tasks_on_host(tasks)

            if not success :
                return False
            
    def start_all_tasks_on_host(self, tasks):
        """
        Listing of all the commands to execute, including the delays 
        before and between the executions.

        @param tasks: list of ids (coh) command_on_host.id
        @type tasks: list

        @return: bool
        
        """
        logging.getLogger().info("<scheduler> : All tasks will be executed at %s seconds" % str(self.FIRST_DELAY))

        sleep(self.FIRST_DELAY)

        for id in tasks :

            try :
                self.proxy.msc.start_command_on_host(id)

            except Exception, err :

                logging.getLogger().error("<scheduler> : Error while executing 'msc.start_command_on_host'")
                logging.getLogger().error("<scheduler> : %s" % err)                        
                return False

            logging.getLogger().info("<scheduler> : Task id (coH): %s executed on host(uuid=%s)" % (str(id), self.uuid))
            sleep(self.BETWEEN_TASKS_DELAY)

        return True

