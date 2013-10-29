# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com
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
"""

import logging
from os import chmod
from weasyprint import HTML, CSS
from importlib import import_module

from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.plugins.base import LdapUserGroupControl
from mmc.plugins.report.config import ReportConfig
from mmc.plugins.report.manager import ReportManager
from mmc.plugins.report.database import ReportDatabase
from mmc.plugins.report.XlsGenerator import XlsGenerator

VERSION = "0.0.0"
APIVERSION = "0:1:0"
REVISION = ""

logger = logging.getLogger()

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    config = ReportConfig("report")
    if config.disabled:
        logger.warning("Plugin report: disabled by configuration.")
        return False
    if not ReportDatabase().activate(config):
        logger.error("Report database not activated")
        return False

    return True

## XMLRPC Methods

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        s.userdn = LdapUserGroupControl().searchUserDN(self.userid)
        return s

#class ContextMaker(ContextMakerI):
#    def getContext(self):
#        s = SecurityContext()
#        s.userid = self.userid
#        s.locationsCount = ComputerLocationManager().getLocationsCount()
#        s.userids = ComputerLocationManager().getUsersInSameLocations(self.userid)
#        s.filterType = "mine"
#        return s

class RpcProxy(RpcProxyI):
    def getAllReports(self):
        """
        XMLRPC method to get All activated reports
        """
        RM = ReportManager()
        if RM.report is None:
            RM.registerReports()
        return RM.report

    def feed_database(self):
        """
        Search all plugins with report and feed their database
        """
        for plugin in self.getAllReports():
            logging.getLogger().debug('Report: I will feed report database of %s plugin', plugin)
            # Get database.py from mmc plugin
            plugin_db = import_module('.'.join(['mmc.plugins', plugin, 'database']))
            # And get its ReportDatabase class
            report_db = getattr(plugin_db, 'ReportDatabase')
            # Call feed_db method
            report_db().feed_db()

    def get_report_datas(self, plugin, report_name, method, args):
        """
        Method to get a report result.
        Give plugin, report_name, method to call, optionaly  args and kargs 
        for this method

        @param plugin: mmc plugin name (aka pkgs, imaging, glpi, ...)
        @type plugin: str
        @param report_name: report class name
        @type report_name: str
        @param method: report class method to be called
        @type method: str
        @return: report method result
        """
        args, kargs = args
        if not kargs:
            kargs = {}
        #Add context to kargs
        kargs['ctx'] = self.currentContext
        report_name = report_name.split('.')
        report_class = report_name.pop()
        report = import_module('.'.join(['mmc.plugins', plugin, 'report'] + report_name))
        r = getattr(report, report_class)()
        m = getattr(r, method)
        return m(*args, **kargs)

    def get_xls_report(self, reports):
        """
        method to get xls report
        """
        xls = XlsGenerator()
        plugins = reports.keys()
        plugins.sort()
        for plugin in plugins:
            for (title, params) in reports[plugin].iteritems():
                if len(params) == 4:
                    params.append({})
                plugin, report_name, method, args, kargs = params
                datas = self.get_report_datas(plugin, report_name, method, (args, kargs))

                kargs['title'] = title
                xls.get_xls_sheet(datas, *args, **kargs)

        return xls.save()

    def get_pdf_report(self, reports):
        # Front page
        front = HTML(string='<h1>Report</h1>').render()
        # Summary
        summary = HTML(string='<p>Summary</p>').render()

        html = ''

        plugins = reports.keys()
        plugins.sort()
        for plugin in plugins:
            for (title, params) in reports[plugin].iteritems():
                if len(params) == 4:
                    params.append({})
                plugin, report_name, method, args, kargs = params
                kargs['title'] = title
                kargs['html'] = html
                html = self.get_report_datas(plugin, report_name, method + '_pdf', (args, kargs))


        css = CSS(string="""
                  table {
                   border-width:1px; 
                   border-style:solid; 
                   border-color:black;
                   border-collapse:collapse;
                  font-size: 10px;
                  font-weight: normal;
                  text-align: center;
                 }
                  td {
                 }
                  td, th {
                   border-width:1px; 
                   border-style:solid; 
                   border-color:black;
                 }
                 """
                 )
        content = HTML(string=html).render(stylesheets=[css])

        # PDF report is a list of all documents
        pdf_report = [front, summary, content]

        # To make one PDF report, we have to get all pages of all documents...
        # First step , we obtain a list of sublists like this :
        # [
        #     [doc1.page1, doc1, page2],
        #     [doc2.page1, doc2.page2],
        #     [doc3.page1, doc3.page2, doc3.page3]
        # ]

        all_pages = [doc.pages for doc in pdf_report]

        # Second step, clean sublist and make a simple list
        # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
        all_pages = [item for sublist in all_pages for item in sublist]

        # ...And combine these pages into a single report Document
        pdf_report[0].copy(all_pages).write_pdf('/tmp/report.pdf')

        chmod('/tmp/report.pdf', 0644)
        return '/tmp/report.pdf'

    def get_svg_file(self, params):
        plugin, report_name, method, args, kargs = params
        r = self.get_report_datas(plugin, report_name, method, (args, kargs))
        return r
