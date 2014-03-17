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
Report plugin for the MMC agent
"""
import logging
import time
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import gettext
from gettext import bindtextdomain

logger = logging.getLogger()

#try:
    #from pulse2.managers.location import ComputerLocationManager
#except ImportError:
    #logger.warn("report: I can't load Pulse ComputerLocationManager")
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.core.tasks import TaskManager
from mmc.core.version import scmRevision
from mmc.plugins.base import LdapUserGroupControl
from mmc.plugins.report.config import ReportConfig, reportconfdir
from mmc.plugins.report.database import ReportDatabase
from mmc.plugins.report.output import XLSGenerator, PDFGenerator, SVGGenerator

VERSION = "3.1.1"
APIVERSION = "0:1:0"
REVISION = scmRevision("$Rev$")

localedir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "locale")

TRANSLATE_ATTRS = ("title", "value")
TRANSLATE_ELEMS = ("homepage", "h1", "h2", "h3", "p", "header", "footer", "left", "right", "center")
_gettext = None


def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def _T(text):
    return _gettext(text).decode('utf8')


def activate():
    config = ReportConfig("report")
    if config.disabled:
        logger.warning("Plugin report: disabled by configuration.")
        return False
    if not ReportDatabase().activate(config):
        logger.error("Report database not activated")
        return False
    # Add historization task in the task manager
    TaskManager().addTask("report.historize_all",
                          (ReportDatabase().historize_all,),
                          cron_expression=config.historization)
    # Import indicators from XML
    import_indicators()
    return True


def import_indicators():
    config = ReportConfig("report")
    xmltemp = ET.parse(os.path.join(reportconfdir, config.indicators)).getroot()

    # Indicator names list
    available_indicators = []

    for module in xmltemp.getiterator('module'):
        module_name = module.attrib['name']
        for indicator in module.getiterator('indicator'):
            indicator_attr = indicator.attrib
            indicator_attr['module'] = module_name
            available_indicators.append(indicator_attr['name'])
            # Add indicator if not exists
            ReportDatabase().add_indicator(indicator_attr)

    # Disable all deleted indicators
    ReportDatabase().disable_indicators_by_name(excludes=available_indicators)
    return True


def translate_attrs(attrs):
    for key, value in attrs.items():
        if key in TRANSLATE_ATTRS:
            attrs[key] = _T(value)
    return attrs


def setup_lang(lang):
    global _gettext
    logger.debug("Using localedir %s" % localedir)
    bindtextdomain("templates", localedir)
    try:
        lang = gettext.translation('templates', localedir, [lang], fallback = True)
        lang.install()
        _gettext = lang.gettext
    except IOError:
        logger.exception("Failed to load langage file")
        pass


class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        s.userdn = LdapUserGroupControl().searchUserDN(self.userid)
        return s


class RpcProxy(RpcProxyI):
    def __init__(self, *args):
        RpcProxyI.__init__(self, *args)
        self.config = ReportConfig("report")

    def calldb(self, func, *args, **kw):
        return getattr(ReportDatabase(), func).__call__(*args, **kw)

    def get_report_sections(self, lang):
        setup_lang(lang)

        def _fetchItems(container):
            result = []
            for item in container:
                attr = translate_attrs(item.attrib)
                result.append(attr)
                attr['items'] = _fetchItems(item)
            return result

        result = {}
        xmltemp = ET.parse(os.path.join(reportconfdir, 'templates', self.config.reportTemplate)).getroot()
        for section in xmltemp.getiterator('section'):
            attr_section = translate_attrs(section.attrib)
            if not attr_section['module'] in result:
                result[attr_section['module']] = []
            # Adding item to attr
            #attr_section['items'] = _fetchItems(section)
            attr_section['tables'] = []
            for table in section.getiterator('table'):
                dct = translate_attrs(table.attrib)
                dct['items'] = _fetchItems(table)
                attr_section['tables'].append(dct)
            result[attr_section['module']].append(attr_section)
        return result

    def generate_report(self, period, sections, tables, items, entities, lang):
        setup_lang(lang)
        indent_str = ''

        entities = [int(str(entity).replace('UUID', '')) for entity in entities]

        temp_path = '/var/tmp/'
        report_path = os.path.join(temp_path, 'report-%d' % int(time.time()))
        pdf_path = os.path.join(report_path, 'report.pdf')
        xls_path = os.path.join(report_path, 'report.xls')
        svg_path = os.path.join(report_path, 'svg')
        os.mkdir(report_path)
        os.mkdir(svg_path)
        os.chmod(report_path, 511)
        os.chmod(svg_path, 511)
        result = {'sections': []}
        #try:
            #getLocationName = ComputerLocationManager().getLocationName
            #entity_names = dict([(location, getLocationName([location]).decode('utf-8')) for location in entities])
        #except NameError:
            #logger.warn("Pulse ComputerLocationManager() not loaded")
            #entity_names = {}
        # Parsing report XML
        xmltemp = ET.parse(os.path.join(reportconfdir, 'templates', self.config.reportTemplate)).getroot()
        if xmltemp.tag != 'template':
            logger.error('Incorrect XML')
            return False
        # xmltemp.attrib ??? if necessary ?? ==> date and time format

        # Setting default params
        locale = {}
        locale['DATE_FORMAT'] = '%Y/%m/%d'

        # Filling global pdf_vars
        pdf_vars = {
            '__USERNAME__': self.currentContext.userid,
            '__COMPANY__': self.config.company,
            '__COMPANY_LOGO_PATH__': self.config.company_logo_path,
            '__PULSE_LOGO_PATH__': self.config.pulse_logo_path,
        }

        xls = XLSGenerator(path=xls_path)
        pdf = PDFGenerator(path=pdf_path, locale=locale)

        def _hf_format(str):
            """
            _hf_format for header-footer format
            Add needed double-quotes and replace PDF variables with
            good values

            @return: well formated content for header or footer
            """
            str = _T(str)
            if str.count('###css_counter###') == 2:
                # 1st css_counter is current page
                str = str.replace('###css_counter###', '" counter(page) "', 1)
                #2nd css_counter is CSS total pages count
                str = str.replace('###css_counter###', '" counter(pages) "', 1)
                if not str.startswith('counter(page)'):
                    str = '"' + str
                if not str.endswith('counter(pages)'):
                    str = str + '"'
            else:
                str = '"' + str + '"'
            return _replace_pdf_vars(str)

        def _hf_feeder(tag):
            """
            This function feed header or footer

            @param tag: XML tag content (header or footer)
            @type tag: xml object

            @param to_feed: item who will be feeded: header or footer
            @type to_feed: str
            """
            for entry in tag:
                if 'logo' in entry.attrib:
                    logo = entry.attrib['logo']
                    background_css = """
                    background: url(%s);
                    background-repeat: no-repeat;
                    background-size: Auto 50px;
                    width: 200px;
                    """ % _replace_pdf_vars(logo)
                    try:
                        setattr(pdf, '_'.join([tag.tag, entry.tag, 'background']), background_css)
                    except Exception, e:
                        logging.getLogger().warn("Something were wrong where setting background for %s: tag is %s", entry.tag, tag.tag)
                        logging.getLogger().warn("Exception: %s", e)
                if entry.text is not None:
                    try:
                        setattr(pdf, '_'.join([tag.tag, entry.tag]), _hf_format(entry.text))
                    except Exception, e:
                        logging.getLogger().warn("Something were wrong where feeding %s: tag is %s", entry.tag, tag.tag)
                        logging.getLogger().warn("Exception: %s", e)

        def _localization(loc_tag):
            for entry in loc_tag:
                if entry.tag.lower() != 'entry':
                    continue
                locale[entry.attrib['name']] = _T(entry.attrib['value'])

            # Setting Period start and period end PDF var
            pdf_vars['__PERIOD_START__'] = datetime.strptime(period[0], "%Y-%m-%d").strftime(locale['DATE_FORMAT'])
            pdf_vars['__PERIOD_END__'] = datetime.strptime(period[-1], "%Y-%m-%d").strftime(locale['DATE_FORMAT'])
            pdf_vars['__NOW_DATE__'] = datetime.now().strftime(locale['DATE_FORMAT'])
            pdf_vars['__NOW_HOUR__'] = datetime.now().strftime('%H:%M:%S')

        def _replace_pdf_vars(text):
            for key in pdf_vars:
                text = text.replace(key, pdf_vars[key])
            return text

        def _h1(text):
            pdf.h1(_T(text))

        def _h2(text):
            pdf.h2(_T(text))

        def _h3(text):
            pdf.h3(_T(text))

        def _html(text):
            #TODO: Add vars replacers
            pdf.pushHTML(_replace_pdf_vars(text))

        def _homepage(text):
            pdf.pushHomePageHTML(_replace_pdf_vars(_T(text)))

        def _sum_None(lst):
            result = None
            for x in lst:
                if x is not None:
                    if result is not None:
                        result += x
                    else:
                        result = x
            return result

        def _periodDict(item_root):
            data_dict = {'titles': [], 'dates': [], 'values': []}
            for date in period:
                ts_min = int(time.mktime(datetime.strptime(date, "%Y-%m-%d").timetuple()))
                formatted_date = datetime.fromtimestamp(ts_min).strftime(locale['DATE_FORMAT'])
                data_dict['dates'].append(formatted_date)
                data_dict['values'].append([])

            def _fetchSubs(container, parent=None, level=-1):
                # If no subelements in container, return
                if len(container) == 0:
                    return (0, None)
                # Adding titles
                GValues = []
                selected_items = 0
                for item in container:
                    indicator_selected = 0
                    if item.tag.lower() != 'item':
                        continue
                    indicator_name = item.attrib['indicator']
                    #if items and not indicator_name in items: continue
                    if not items or indicator_name in items:
                        data_dict['titles'].append(indent_str * level + ' ' + _T(item.attrib['title']))
                        indicator_selected = 1
                    # temp list to do arithmetic operations
                    values = []
                    for i in xrange(len(period)):
                        date = period[i]
                        # Creating a timestamp range for the specified date
                        ts_min = int(time.mktime(datetime.strptime(date, "%Y-%m-%d").timetuple()))
                        ts_max = ts_min + 86400   # max = min + 1day (sec)
                        #
                        value = ReportDatabase().get_indicator_value_at_time(indicator_name, ts_min, ts_max, entities)
                        values.append(value)
                        # if item is not selected, don't add value to the Data Dict
                        if not items or indicator_name in items:
                            data_dict['values'][i].append(value)
                    # If item is not selected don't add values to arithmetic table list
                    #
                    if items and not indicator_name in items:
                        (subCount, childGValues) = _fetchSubs(item, container, level + 1)
                        if subCount != 0:
                            GValues.append(values)
                            indicator_selected = 1
                    else:
                        # If parent is checked, we don't look at childs
                        (subCount, childGValues) = (0, None)
                        GValues.append(values)
                    # Calcating "other" line if indicator type is numeric
                    if ReportDatabase().get_indicator_datatype(indicator_name) == 0 and subCount != 0:
                        #and (not items or indicator_name in items):
                        data_dict['titles'].append(indent_str * (level + 1) +
                                                   ' %s (%s)' %
                                                   (_T(item.attrib['title']),
                                                    locale['STR_OTHER']))
                        for i in xrange(len(period)):
                            child_sum = _sum_None([l[i] for l in childGValues])
                            if child_sum is not None and values[i] is not None:
                                other_value = values[i] - child_sum
                            else:
                                other_value = None
                            #print other_value
                            data_dict['values'][i].append(other_value)
                    if indicator_selected != 0:
                        selected_items += 1
                return (selected_items, GValues)
            _fetchSubs(item_root)
            return data_dict

        def _keyvalueDict(item_root):
            data_dict = {'headers': [locale['STR_KEY'], locale['STR_VALUE']], 'values': []}

            def _fetchSubs(container, parent=None, level=-1, parent_value=0):
                values = []
                for item in container:
                    if item.tag.lower() != 'item':
                        continue
                    indicator_name = item.attrib['indicator']
                    indicator_label = _T(item.attrib['title'])
                    indicator_value = ReportDatabase().get_indicator_current_value(indicator_name, entities)
                    # indicator_value is a list of dict {'entity_id' : .., 'value' .. }
                    # ==============================================================
                    # ==> Generate one entry for each entity [disabled]
                    #for entry in indicator_value:
                    #    if entry['entity_id'] in entity_names:
                    #        entity_name = entity_names[entry['entity_id']]
                    #    else:
                    #        entity_name = entry['entity_id']
                    #    if not items or indicator_name in items:
                    #        data_dict['values'].append([ indent_str * level + indicator_label + (' (%s)' % entity_name ), entry['value']])
                    # =================================================================
                    # Calculating sum value for entities
                    value = _sum_None([x['value'] for x in indicator_value])
                    values.append(value)
                    if not items or indicator_name in items:
                        data_dict['values'].append([indent_str * level + indicator_label, value])

                    # TODO: Calculate other cols
                    # Fetch this item subitems
                    _fetchSubs(item, container, level + 1, value)
                # Generating others value
                if parent and values:
                    others_value = parent_value - _sum_None(values)
                    data_dict['values'].append([indent_str * level +
                                                ' %s (%s)' %
                                                (parent.attrib['title'],
                                                 locale['STR_OTHER']),
                                                others_value])
            _fetchSubs(item_root)
            return data_dict

        def _period_None_to_empty_str(data):
            from copy import deepcopy
            datas = deepcopy(data)
            for i in xrange(len(datas['titles'])):
                for v in datas['values']:
                    if v[i] is None:
                        v[i] = ''
            return datas

        def _keyval_None_to_empty_str(data):
            from copy import deepcopy
            datas = deepcopy(data)
            for line in datas['values']:
                for td in line:
                    td = td if td is not None else ''
            return datas

        # Browsing all childs
        for level1 in xmltemp:
            attr1 = translate_attrs(level1.attrib)
            ## =========< localization strings >===================
            if level1.tag.lower() == 'localization':
                _localization(level1)
            ## =========< H1 >===================
            if level1.tag.lower() == 'h1':
                _h1(level1.text)
            ## =========< H2 >===================
            if level1.tag.lower() == 'h2':
                _h2(level1.text)
            ## =========< H3 >===================
            if level1.tag.lower() == 'h3':
                _h3(level1.text)
            ## =========< HTML >===================
            if level1.tag.lower() == 'html':
                _html(level1.text)
            ## =========< HTML >===================
            if level1.tag.lower() == 'homepage':
                _homepage(level1.text)
            if level1.tag.lower() in ['footer', 'header']:
                _hf_feeder(level1)
            ## =========< SECTION >===================
            if level1.tag.lower() == 'section':
                # Checking if section is present in sections
                # else we skip it
                if not attr1['name'] in sections:
                    continue
                section_data = {'title': attr1['title'], 'content': []}
                # Printing section
                for level2 in level1:
                    attr2 = translate_attrs(level2.attrib)
                    ## =========< TABLE >===================
                    if level2.tag.lower() == 'table':
                        # Checking if table is present in tables
                        # else we skip it
                        if not attr2['name'] in tables:
                            continue
                        # printing table items
                        if attr2['type'] == 'period':
                            data_dict = _periodDict(level2)   # period table type
                            data_dict_without_none = _period_None_to_empty_str(data_dict)
                        elif attr2['type'] == 'key_value':
                            data_dict = _keyvalueDict(level2)   # key/value type
                            data_dict_without_none = _keyval_None_to_empty_str(data_dict)

                        # Push table to PDF and XLS
                        xls.pushTable(attr2['title'], data_dict)
                        pdf.pushTable(attr2['title'], data_dict)

                        # Add table to result dict [to interface]
                        section_data['content'].append({
                            'type': 'table',
                            'data': data_dict_without_none,
                            'title': attr2['title']
                        })

                        if 'chart_type' in attr2:
                            # Generatinng SVG
                            svg_filename = attr1['name'] + '_' + attr2['name']
                            svg_filepath = os.path.join(svg_path, svg_filename)
                            svg = SVGGenerator(path=svg_filepath, locale=locale, extra_css=self.config.graphCSS)
                            if attr2['chart_type'] == 'line':
                                svg.lineChart(attr2['title'], data_dict)
                            elif attr2['chart_type'] == 'bar':
                                svg.barChart(attr2['title'], data_dict)
                            elif attr2['chart_type'] == 'pie':
                                svg.pieChart(attr2['title'], data_dict)
                            # Insert SVG into the PDF
                            pdf.pushSVG(svg.toXML())
                            section_data['content'].append({
                                'type': 'chart',
                                'svg_path': svg_filepath + '.svg',
                                'png_path': svg_filepath + '.png'
                            })
                            # Save SVG files (SVG/PNG)
                            svg.save()

                result['sections'].append(section_data)

        # Saving outputs
        xls.save()
        pdf.save()
        result['pdf_path'] = pdf_path
        result['xls_path'] = xls_path
        return result

    def historize_all(self, timestamp=None):
        # If timestamp is not specified, taking actual time
        if timestamp is None:
            timestamp = int(time.time())
        ReportDatabase().historize_all(timestamp)
        
    def historize_overwrite_last(self, timestamp=None):
        # If timestamp is not specified, taking actual time
        if not timestamp:
            timestamp = int(time.time())
        ReportDatabase().historize_overwrite_last(timestamp)

    def get_indicator_value_at_time(self, indicator_name, ts_min, ts_max, entities=[]):
        return ReportDatabase().get_indicator_value_at_time(indicator_name, ts_min, ts_max, entities)

    def get_indicator_current_value(self, indicator_name, entities=[]):
        return ReportDatabase().get_indicator_current_value(indicator_name, entities)
