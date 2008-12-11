#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id: __init__.py 195 2007-09-10 08:20:59Z cedric $
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

# Misc            
import re    
import logging
import pwd
import grp  
import string

# MMC
from pulse2.database.config import DatabaseConfig

class InventoryDatabaseConfig(DatabaseConfig):
    displayLocalisationBar = False
    list = {
            'Software/ProductName':['string'],
            'Hardware/ProcessorType':['string'],
            'Hardware/OperatingSystem':['string'],
            'Drive/TotalSpace':['int']
    }
    double = {
            'Software/Products': [
                ['Software/ProductName', 'string'],
                ['Software/ProductVersion', 'int']
            ]
    }
    doubledetail = {
            'Software/ProductVersion' : 'int'
    }
    halfstatic = {
            'Registry/Value/display name' : ['string', 'Path', 'DisplayName']
    }
    
    expert_mode = {}
    graph = {}
    display = [['cn', 'Computer Name'], ['displayName', 'Description']]
    content = {}

    dbname = "inventory"

    def setup(self, config_file):
        # read the database configuration
        DatabaseConfig.setup(self, config_file)

        # read the other inventory default parameters
        if self.cp.has_section("graph"):
            for i in self.getInventoryParts():
                if self.cp.has_option("graph", i):
                    self.graph[i] = self.cp.get("graph", i).split('|')
                else:
                    self.graph[i] = []
                if self.cp.has_option("expert_mode", i):
                    self.expert_mode[i] = self.cp.get("expert_mode", i).split('|')
                else:
                    self.expert_mode[i] = []

        if self.cp.has_option('main', 'displayLocalisationBar'):
            self.displayLocalisationBar = self.cp.getboolean('main', 'displayLocalisationBar')


        if self.cp.has_section("computers"):
            if self.cp.has_option("computers", "display"):
                self.display = map(lambda x: x.split('::'), self.cp.get("computers", "display").split('||'))
    
    
            # Registry::Path::path||Registry::Value::srvcomment::Path==srvcomment
            if self.cp.has_option("computers", "content"):
                for c in map(lambda x: x.split('::'), self.cp.get("computers", "content").split('||')):
                    if not self.content.has_key(c[0]):
                        self.content[c[0]] = []
                    self.content[c[0]].append( map(lambda x: desArrayIfUnic(x.split('==')), c[1:]))

        if self.cp.has_section('querymanager'):
            if self.cp.has_option('querymanager', 'list'):
                simple = self.cp.get('querymanager', 'list')
                self.list = {}
                if simple != '':
                    # Software/ProductName||Hardware/ProcessorType||Hardware/OperatingSystem||Drive/TotalSpace
                    for l in simple.split('||'):
                        self.list[l] = ['string'] # TODO also int...
    
            if self.cp.has_option('querymanager', 'double'):
                double = self.cp.get('querymanager', 'double')
                self.double = {}
                if double != '':
                    # Software/Products::Software/ProductName##Software/ProductVersion
                    for l in double.split('||'):
                        name, vals = l.split('::')
                        val1, val2 = vals.split('##')
                        self.double[name] = [[val1, 'string'], [val2, 'string']]
    
            if self.cp.has_option('querymanager', 'halfstatic'):
                halfstatic = self.cp.get('querymanager', 'halfstatic')
                self.halfstatic = {}
                if halfstatic != '':
                    # Registry/Value::Path##DisplayName
                    for l in halfstatic.split('||'):
                        name, vals = l.split('::')
                        k, v = vals.split('##')
                        self.halfstatic[name] = ['string', k, v]

    def getInventoryParts(self):
        """
        @return: Return all available inventory parts
        @rtype: list
        """
        return [ "Bios", "BootDisk", "BootGeneral", "BootMem", "BootPart", "BootPCI", "Controller", "Custom", "Drive", "Hardware", "Input", "Memory", "Modem", "Monitor", "Network", "Port", "Printer", "Slot", "Software", "Sound", "Storage", "VideoCard", "Registry", "Entity" ]
           
    def getInventoryNoms(self, table = None):
        """
        @return: Return all available nomenclatures tables
        @rtype: dict
        """ 
        noms = {
            'Registry':['Path']
        }   
            
        if table == None:
            return noms
        if noms.has_key(table):
            return noms[table]
        return None


def desArrayIfUnic(x):
    if len(x) == 1:
        return x[0]
    return x

                                

