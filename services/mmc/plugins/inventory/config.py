#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id: __init__.py 3 2008-03-03 14:35:11Z cdelfosse $
#
# This file is part of MMC.
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

from mmc.support.config import PluginConfig
from mmc.support.mmctools import Singleton, xmlrpcCleanup
from mmc.plugins.inventory.utilities import getInventoryParts

from ConfigParser import NoOptionError
import logging

class InventoryExpertModeConfig(PluginConfig):

    def readConf(self):
        PluginConfig.readConf(self)
        self.expert_mode = {}
        self.graph = {}
        for i in getInventoryParts():
            try:
                self.graph[i] = self.get("graph", i).split('|')
            except NoOptionError:
                self.graph[i] = []
            try:
                self.expert_mode[i] = self.get("expert_mode", i).split('|')
            except NoOptionError:
                self.expert_mode[i] = []

class InventoryConfig(PluginConfig):
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

    def readConf(self):
        PluginConfig.readConf(self)
        self.dbdriver = self.get("inventory", "dbdriver")
        self.dbhost = self.get("inventory", "dbhost")
        self.dbname = self.get("inventory", "dbname")
        self.dbuser = self.get("inventory", "dbuser")
        self.dbpasswd = self.getpassword("inventory", "dbpasswd")
        self.disable = self.getboolean("main", "disable")
        try:
            self.dbpoolrecycle = self.getint("inventory", "dbpoolrecycle")
        except NoOptionError:
            self.dbpoolrecycle = 60
        try:
            self.dbpoolsize = self.getint("inventory", "dbpoolsize")
        except NoOptionError:
            self.dbpoolsize = 5
                                                                        
        try:
            self.dbport = self.getint("inventory", "dbport")
        except NoOptionError:
            # We will use the default db driver port
            self.dbport = None

        if self.has_option("inventory", "dbsslenable"):
            self.dbsslenable = self.getboolean("inventory", "dbsslenable")
            if self.dbsslenable:
                self.dbsslca = self.get("inventory", "dbsslca")
                self.dbsslcert = self.get("inventory", "dbsslcert")
                self.dbsslkey = self.get("inventory", "dbsslkey")
        else:
            self.dbsslenable = False

        try:
            self.display = map(lambda x: x.split('::'), self.get("computers", "display").split('||'))
        except NoOptionError:
            self.display = [['cn', 'Computer Name'], ['displayName', 'Description']]

        if self.has_option('main', 'displayLocalisationBar'):
            self.displayLocalisationBar = self.getboolean('main', 'displayLocalisationBar')
            
        try:
            self.content = {}
            
            # Registry::Path::path||Registry::Value::srvcomment::Path==srvcomment
            for c in map(lambda x: x.split('::'), self.get("computers", "content").split('||')):
                if not self.content.has_key(c[0]):
                    self.content[c[0]] = []
                self.content[c[0]].append( map(lambda x: desArrayIfUnic(x.split('==')), c[1:]))
        except NoOptionError:
            self.content = {}

        if self.has_option('querymanager', 'list'):
            simple = self.get('querymanager', 'list')
            self.list = {}
            if simple != '':
                # Software/ProductName||Hardware/ProcessorType||Hardware/OperatingSystem||Drive/TotalSpace
                for l in simple.split('||'):
                    self.list[l] = ['string'] # TODO also int...

        if self.has_option('querymanager', 'double'):
            double = self.get('querymanager', 'double')
            self.double = {}
            if double != '':
                # Software/Products::Software/ProductName##Software/ProductVersion
                for l in double.split('||'):
                    name, vals = l.split('::')
                    val1, val2 = vals.split('##')
                    self.double[name] = [[val1, 'string'], [val2, 'string']]
                
        if self.has_option('querymanager', 'halfstatic'):
            halfstatic = self.get('querymanager', 'halfstatic')
            self.halfstatic = {}
            if halfstatic != '':
                # Registry/Value::Path##DisplayName
                for l in halfstatic.split('||'):
                    name, vals = l.split('::')
                    k, v = vals.split('##')
                    self.halfstatic[name] = ['string', k, v]


def desArrayIfUnic(x):
    if len(x) == 1:
        return x[0]
    return x
