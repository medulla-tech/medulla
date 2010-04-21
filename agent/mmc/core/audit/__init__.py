# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Factory used to interact with the Audit module
(read/write audit logs)
"""

from mmc.support.mmctools import Singleton
from mmc.core.audit.writernull import AuditWriterNull

class AuditFactory(Singleton):

    def __init__(self, config = None, init = True):
        Singleton.__init__(self)
        if not hasattr(self, 'logaction'):
            if config == None:
                from mmc.plugins.base import BasePluginConfig
                try:
                    # Read the configuration
                    self.make(BasePluginConfig('base'), init)
                except IOError:
                    # Fallback on default configuration
                    self.make(None, init)
            else:
                self.make(config, init)

    def make(self, config, init = True):
        """
        Configure the logging mode database,none,syslog
        @param config: confile .ini
        @type config: ConfigParser
        """
        if config and config.auditmethod == "database":
            from mmc.core.audit.writers import AuditWriterDB
            AuditWriterDB().setConfig(config)
            if init:
                AuditWriterDB().init(config.auditdbdriver, config.auditdbuser, config.auditdbpassword, config.auditdbhost, config.auditdbport, config.auditdbname)
            self.logaction = AuditWriterDB()
        else:
            self.logaction = AuditWriterNull()

        return self.logaction

    def getAuditInstance(self):
        """
        Return the object built by the factory to log events
        """
        return self.logaction
    
    def log(self,*args):
        """
        Log Actions
        @param **args : list of log args
        """
        return self.logaction.log(*args)
  
    def getLog(self,*args):
        """
        Get Log Actions return a listEvent
        @param *args : list of log filter args
        """
        return self.logaction.getLog(*args)
    
    def getLogById(self,*args):
        """
        Get Log Actions return an Event
        @param *args : list of log filter args
        """
        return self.logaction.getLogById(*args)
    
    def getActionType(self,*args):
        """
        Get Log Actions return an list of actions or type
        @param action : return actions
        @param type : return type
        """
        return self.logaction.getActionType(*args)
        
    def setup(self,*args):
        """
        Setup database default values and set actions list for the module (MODULE_NAME)
        """
        self.logaction.setup(*args)
    
    def commit(self):
        """
        Set result in log table to True
        """
        self.logaction.commit()

