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
import time
import os
import datetime
from importlib import import_module

from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.plugins.base import LdapUserGroupControl
from mmc.plugins.report.config import ReportConfig
from mmc.plugins.report.manager import ReportManager
from mmc.plugins.report.database import ReportDatabase
import xml.etree.ElementTree as ET
from mmc.plugins.report.output import XlsGenerator, PdfGenerator, SvgGenerator

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

                xls.pushTable(title, datas)

        return xls.save()

    def get_pdf_report(self, reports, graph = True):
        pdf = PdfGenerator()

        plugins = reports.keys()
        plugins.sort()
        for plugin in plugins:
            for (title, params) in reports[plugin].iteritems():
                if len(params) == 4:
                    params.append({})
                plugin, report_name, method, args, kargs = params
                datas = self.get_report_datas(plugin, report_name, method, (args, kargs))
                datas_copy = datas.copy()
                pdf.pushTable(title, datas)
                if graph:
                    svg = SvgGenerator()
                    svg.barChart(datas_copy)
                    pdf.pushSVG(svg.toXML())

        return pdf.save()

    def get_svg_file(self, params):
        plugin, report_name, method, args, kargs = params
        r = self.get_report_datas(plugin, report_name, method, (args, kargs))
        return r


    def calldb(self, func, *args, **kw):
        return getattr(ReportDatabase(),func).__call__(*args, **kw)

    def get_report_sections(self, lang):
        result = {}
        xmltemp = ET.parse('/etc/mmc/pulse2/report/templates/%s.xml' % lang).getroot()
        for section in xmltemp.iter('section'):
            attr = section.attrib
            if not attr['module'] in result:
                result[attr['module']] = []
            result[attr['module']].append(attr)
        return result

    def generate_report(self, period, sections, entities, lang):
        #
        temp_path = '/var/tmp/'
        report_path = os.path.join(temp_path, 'report-%d' % int(time.time()))
        pdf_path = os.path.join(report_path, 'report.pdf')
        xls_path = os.path.join(report_path, 'report.xls')
        os.mkdir(report_path)
        os.chmod(report_path, 511)
        #TODO : Chmod this path
        xls = XlsGenerator(path = xls_path)
        pdf = PdfGenerator(path = pdf_path)
        result = {}
        #
        # TODO : Get entity names from entity uuids
        entity_names = entities
        # Parsing report XML
        xmltemp = ET.parse('/etc/mmc/pulse2/report/templates/%s.xml' % lang).getroot()
        if xmltemp.tag != 'template':
            logging.getLogger().error('Incorrect XML')
            return False
        # xmltemp.attrib ??? if necessary ?? ==> date and time format
        #TODO: Read date format from XML
        date_format = '%d/%m/%Y'

        def _h1(text):
            # send text to pdf, html, ...
            pass

        def _h2(text):
            # send text to pdf, html, ...
            pass

        def _periodDict(item_container, title = ''):
            data_dict = {'titles' : [], 'dates' : [], 'values' : [] }
            indicators = []
            for item in item_container:
                if item.tag.lower() != 'item' : continue
                indicator_name = item.attrib['indicator']
                data_dict['titles'].append(item.attrib['title'])
                indicators.append(item.attrib['indicator'])
            for date in period:
                # Creating a timestamp range for the specified date
                ts_min = int(time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple()))
                ts_max = ts_min + 86400 # max = min + 1day (sec)
                #
                formatted_date = datetime.datetime.fromtimestamp(ts_min).strftime(date_format)
                data_dict['dates'].append(formatted_date)
                values = []
                for indicator in indicators:
                    values.append(ReportDatabase().get_indicator_value_at_time(indicator, ts_min, ts_max, entities))
                data_dict['values'].append(values)
            logging.getLogger().warning('GOT PERIOD DICT')
            logging.getLogger().warning(data_dict)
            return data_dict

        def _keyvalueDict(item_container, title = ''):
            #TODO : implement importign Clé, Valeur string from XML
            data_dict = {'headers' : ['Key','Value'], 'values' : []}
            indicators = []
            for item in item_container:
                if item.tag.lower() != 'item' : continue
                indicator_name = item.attrib['indicator']
                indicator_label = item.attrib['title']
                indicator_value = ReportDatabase().get_indicator_current_value(indicator_name, entities)
                # indicator_value is a list of dict {'entity_id' : .., 'value' .. }
                for entry in indicator_value:
                    # TODO: Print entity names not UUIDs
                    data_dict['values'].append([indicator_label + (' (%s)' % entry['entity_id'] ), entry['value']])
            logging.getLogger().warning('GOT KEY/VALUE DICT')
            logging.getLogger().warning(data_dict)
            return data_dict

        # Browsing all childs
        for level1 in xmltemp:
            attr1 = level1.attrib
            ## =========< H1 >===================
            if level1.tag.lower() == 'h1':
                _h1(level1.text)
            ## =========< H2 >===================
            if level1.tag.lower() == 'h2':
                _h2(level1.text)
            ## =========< SECTION >===================
            if level1.tag.lower() == 'section':
                # Checking if section is present in sections
                # else we skip it
                if not attr1['name'] in sections:
                    continue
                # Printing section
                for level2 in level1:
                    attr2 = level2.attrib
                    ## =========< TABLE >===================
                    if level2.tag.lower() == 'table':
                        # printing table items
                        # ====> PERIOD TABLE TYPE
                        if attr2['type'] == 'period':
                            data_dict = _periodDict(level2)
                            # ==> TO PDF
                            # ==> to XLS
                            xls.pushTable(attr2['title'], data_dict)
                            pdf.pushTable(attr2['title'], data_dict)
                        # ====> KEY-VALUE TABLE TYPE
                        if attr2['type'] == 'key_value':
                            data_dict = _keyvalueDict(level2)
                            # ==> TO PDF
                            # ==> to XLS
                            xls.pushTable(attr2['title'], data_dict)
                            pdf.pushTable(attr2['title'], data_dict)
                    ## =========< CHART >===================
                    if level2.tag.lower() == 'chart':
                        # printing table items
                        # ====> PERIOD TABLE TYPE
                        if attr2['type'] == 'period':
                            data_dict = _periodDict(level2)
                            # ==> to SVG (handle cases)
                        # ====> KEY-VALUE TABLE TYPE
                        if attr2['type'] == 'key_value':
                            data_dict = _keyvalueDict(level2)
                            # ==> to SVG (handle cases)

        # Saving outputs
        xls.save()
        pdf.save()
        result['pdf_path'] = pdf_path
        result['xls_path'] = xls_path
        return result












