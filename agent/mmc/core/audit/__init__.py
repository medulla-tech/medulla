# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Factory used to interact with the Audit module
(read/write audit logs)
"""

from mmc.support.mmctools import Singleton
from mmc.core.audit.writernull import AuditWriterNull


class AuditFactory(Singleton):
    def __init__(self, config=None, init=True):
        Singleton.__init__(self)
        if not hasattr(self, "logaction"):
            if config == None:
                from mmc.plugins.base import BasePluginConfig
                from mmc.support.config import PluginConfigFactory

                try:
                    # Read the configuration
                    self.make(PluginConfigFactory.new(BasePluginConfig, "base"), init)
                except IOError:
                    # Fallback on default configuration
                    self.make(None, init)
            else:
                self.make(config, init)

    def make(self, config, init=True):
        """
        Configure the logging mode database,none,syslog
        @param config: confile .ini
        @type config: ConfigParser
        """
        if config and config.auditmethod == "database":
            from mmc.core.audit.writers import AuditWriterDB

            AuditWriterDB().setConfig(config)
            if init:
                AuditWriterDB().init(
                    config.auditdbdriver,
                    config.auditdbuser,
                    config.auditdbpassword,
                    config.auditdbhost,
                    config.auditdbport,
                    config.auditdbname,
                )
            self.logaction = AuditWriterDB()
        else:
            self.logaction = AuditWriterNull()

        return self.logaction

    def getAuditInstance(self):
        """
        Return the object built by the factory to log events
        """
        return self.logaction

    def log(self, *args):
        """
        Log Actions
        @param **args : list of log args
        """
        return self.logaction.log(*args)

    def getLog(self, *args):
        """
        Get Log Actions return a listEvent
        @param *args : list of log filter args
        """
        return self.logaction.getLog(*args)

    def getLogById(self, *args):
        """
        Get Log Actions return an Event
        @param *args : list of log filter args
        """
        return self.logaction.getLogById(*args)

    def getActionType(self, *args):
        """
        Get Log Actions return an list of actions or type
        @param action : return actions
        @param type : return type
        """
        return self.logaction.getActionType(*args)

    def setup(self, *args):
        """
        Setup database default values and set actions list for the module (MODULE_NAME)
        """
        self.logaction.setup(*args)

    def commit(self):
        """
        Set result in log table to True
        """
        self.logaction.commit()
