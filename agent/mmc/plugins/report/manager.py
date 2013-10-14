# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2013 Mandriva, http://www.mandriva.com
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

from inspect import getmembers, isclass, ismodule
from importlib import import_module
from mmc.agent import PluginManager
from mmc.support.mmctools import SingletonN

class ReportManager(object):
    __metaclass__ = SingletonN

    def __init__(self):
        self.report = None

    def getActivePlugins(self):
        """
        @return: a list of all enabled mmc plugins
        @rtype: list
        """
        pm = PluginManager()
        return pm.getEnabledPluginNames()

    def getPluginsWithReports(self):
        """
        @return: Get all plugins who contains reports
        @rtype: list
        """
        active_plugins = self.getActivePlugins()
        res = []
        for plugin in active_plugins:
            try:
                import_module('.'.join(['mmc.plugins', plugin, 'report']))
                res.append(plugin)
            except ImportError:
                pass
        return res

    def getPluginReports(self, report_obj, module = ''):
        """
        Return all available reports classes for a given plugin
        /!\: recursive method

        @param: report_obj: a report object
        @type: report_obj: object instance

        @return: a list of all class reports
        @rtype: list of report class instance
        """
        res = []
        if report_obj.__name__ != 'logging':
            for name, obj in getmembers(report_obj):
                if name not in ['ReportDatabase', 'logging', 'datetime', 'pygal', 'Style', 'timedelta', 'ComputerManager']:
                    if ismodule(obj):
                        res = res + self.getPluginReports(obj, name)
                    elif isclass(obj):
                        add_module = True
                        if hasattr(obj, '__enable__'):
                            add_module = obj.__enable__
                        if add_module:
                            # x.strip() to remove empty strings (module's default value)
                            res.append([x for x in [module, name] if x.strip()])
        return res

    def registerReports(self):
        """
        Register all report classes for all enabled plugins
        self.report is a dict with plugin as key and classes instances as value
        """
        self.report = {}
        plugins = self.getPluginsWithReports()
        for plugin in plugins:
            report_obj = import_module('.'.join(['mmc.plugins', plugin, 'report']))
            self.report[plugin] = self.getPluginReports(report_obj)
        return True
