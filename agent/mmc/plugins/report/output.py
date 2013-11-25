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

"""
This module generate XLS, PDF and SVG output files
"""

import os
import xlwt
from weasyprint import HTML, CSS
import pygal
from pygal import Config
from pygal.style import Style
from os import chmod
from base64 import b64encode
import logging

from mmc.plugins.report.config import ReportConfig, reportconfdir


class XLSGenerator(object):
    def __init__(self, path='/tmp/report.xls'):
        self.wbk = xlwt.Workbook()
        self.path = path

    def pushTable(self, title, datas):
        if 'headers' in datas:    # simple sheets
            return self.get_simple_sheet(title, datas)
        else:    # period sheets
            return self.get_period_sheet(title, datas)

    def _clean_sheet_name(self, sheet_name):
        """
        Check if sheet_name is clean
        Replace forbidden characters by underscore
        @see xlwt.Utils.valid_sheet_name()
        """
        if sheet_name == "":
            sheet_name = "Empty name"
        if sheet_name[0] == "'":
            sheet_name = list(sheet_name)
            sheet_name[0] = '_'
            sheet_name = ''.join(sheet_name)
        if len(sheet_name) > 31:
            sheet_name = sheet_name[:31]
        for c in "[]:\\?/*\x00":
            if c in sheet_name:
                sheet_name = sheet_name.replace(c, '_')
        return sheet_name

    def get_simple_sheet(self, sheet_name, datas):
        sheet_name = self._clean_sheet_name(sheet_name)
        sheet = self.wbk.add_sheet(sheet_name)
        line = 0
        column = 0
        # Write headers
        headers = datas['headers']
        for x in xrange(len(headers)):
            sheet.write(line, column + x, headers[x])
        line += 1

        datas = datas['values']
        for x in xrange(len(datas)):
            for y in xrange(len(datas[x])):
                sheet.write(line, column + y, datas[x][y])
            line += 1
        return self.wbk

    def get_period_sheet(self, sheet_name, datas):
        sheet_name = self._clean_sheet_name(sheet_name)
        sheet = self.wbk.add_sheet(sheet_name)

        titles = datas['titles']
        dates = datas['dates']
        values = datas['values']
        line = 0
        column = 0

        sheet.write(line, column, '')
        for i in xrange(len(titles)):
            line += 1
            sheet.write(line, column, datas['titles'][i])
        for i in xrange(len(dates)):
            column += 1
            line = 0
            sheet.write(line, column, dates[i])
            for j in xrange(len(values[i])):
                line += 1
                sheet.write(line, column, values[i][j])
        return self.wbk

    def save(self):
        self.wbk.save(self.path)
        chmod(self.path, 0644)
        return self.path


class PDFGenerator(object):
    def __init__(self, path='/tmp/report.pdf', locale={}):
        self.homepage = ''
        self.summary = ''
        self.config = ReportConfig("report")

        self.content = ''
        self.header_left = ''
        self.header_right = ''
        self.header_center = ''
        self.footer_left = ''
        self.footer_right = ''
        self.footer_left = ''
        self.path = path
        # Localization strings
        self.locale = locale

    def h1(self, str):
        self.content += '<h1>%s</h1>' % str

    def h2(self, str):
        self.content += '<h2>%s</h2>' % str

    def h3(self, str):
        self.content += '<h3>%s</h3>' % str

    def set_header_left(self, str):
        self.header_left = str.strip()

    def set_header_center(self, str):
        self.header_center = str.strip()

    def set_header_right(self, str):
        self.header_right = str.strip()

    def set_footer_left(self, str):
        self.footer_left = str.strip()

    def set_footer_center(self, str):
        self.footer_center = str.strip()

    def set_footer_right(self, str):
        self.footer_right = str.strip()

    @property
    def _css_file_content(self):
        string = ''
        try:
            f = open(os.path.join(reportconfdir, 'css', self.config.reportCSS))
            string = f.read()
            f.close()
        except IOError, e:
            logging.getLogger().warning(e)
        return string

    @property
    def homepage_css(self):
        return CSS(string=self._css_file_content)

    @property
    def content_css(self):
        string = """

        @page {
            counter-increment: page;
            /*margin: 8mm 8mm 15mm 8mm;*/
            /*size: letter;*/

            @top-left {
                content: %s;
                font-size: .75em;
            }

            @top-center {
                content: %s;
                font-size: .75em;
            }

            @top-right {
                content: %s;
                font-size: .75em;
            }

            @bottom-left {
                content: %s;
                font-size: .75em;
                padding-bottom: 6mm;
            }

            @bottom-center {
                content: %s;
                font-size: .75em;
                padding-bottom: 6mm;
            }

            @bottom-right {
                content: %s;
                font-size: .75em;
                padding-bottom: 6mm;
            }
        }
        """ % (
            self.header_left,
            self.header_center,
            self.header_right,
            self.footer_left,
            self.footer_center,
            self.footer_right
        )
        string += self._css_file_content
        return CSS(string=string)

    def get_simple_sheet(self, title, datas):
        self.h3(title)

        headers = datas['headers']
        values = datas['values']

        # Table headers
        self.content += '<table>'
        self.content += '<tr>'
        for h in headers:
            if h == 'titles':
                continue
            self.content += '<th>'
            self.content += h
            self.content += '</th>'
        self.content += '</tr>'

        # Table content
        for line in values:
            self.content += '<tr>'
            for td in line:
                if isinstance(td, (int, float)):
                    td = str(td)
                    if td.endswith('.0'):
                        td = td[:-2]
                self.content += '<td>'
                self.content += td if td is not None else ''
                self.content += '</td>'
            self.content += '</tr>'

        self.content += '</table>'

    def get_period_sheet(self, title, datas):
        self.h3(title)
        titles = datas['titles']
        dates = datas['dates']
        values = datas['values']

        # Table
        self.content += '<table>'
        self.content += '<tr>'
        self.content += '<th>'
        self.content += '</th>'
        for d in dates:
            self.content += '<th>'
            self.content += d
            self.content += '</th>'
        for x in xrange(len(titles)):
            self.content += '<tr>'

            self.content += '<td>'
            self.content += titles[x]
            self.content += '</td>'
            for v in values:
                value = v[x]
                if value is None:
                    value = ''
                elif isinstance(value, (int, float)):
                    value = str(value)
                    if value.endswith('.0'):
                        value = value[:-2]
                self.content += '<td>'
                self.content += value
                self.content += '</td>'

            self.content += '</tr>'

        self.content += '</tr>'
        self.content += '</table>'

    def pushHomePageHTML(self, html):
        self.homepage += html

    def pushHTML(self, html):
        self.content += html

    def pushTable(self, title, datas):
        if 'headers' in datas:   # simple sheets
            return self.get_simple_sheet(title, datas)
        else:   # period sheets
            return self.get_period_sheet(title, datas)

    def pushSVG(self, svg):
        self.content += '<img src="data:image/svg+xml;charset=utf-8;base64,%s" />' % b64encode(svg.encode('utf8'))

    def save(self):
        # PDF report is a list of all documents
        self.summary = '<h1>%s</h1>' % (self.locale['STR_SUMMARY'])

        # To make one PDF report, we have to get all pages of all documents...
        # First step , we obtain a list of sublists like this :
        # [
        #     [doc1.page1, doc1, page2],
        #     [doc2.page1, doc2.page2],
        #     [doc3.page1, doc3.page2, doc3.page3]
        # ]

        # Rendering content
        content = HTML(string=self.content, encoding="utf-8").render(stylesheets=[self.content_css])

        #Priting summary table BEGIN
        self.summary += '<table style="border:0">'

        def _printSummary(bookmarks, indent=0, numer=''):
            for i, (label, (page, _, _), children) in enumerate(bookmarks, 1):
                tr_style = 'style="border-top:1px solid #CCC;border-bottom:1px solid #CCC"'
                title_td_style = 'style="border:0;text-align:left;width:550px;padding:10px;"'
                page_num_td_style = 'style="border:0;width:50px"'
                if indent == 0 and i == 1:
                    tr_style = 'style="border-bottom:1px solid #CCC"'
                self.summary += ('<tr %s><td %s>%s%s. %s</td><td %s>%d</td></tr>' % (
                    tr_style, title_td_style, '&nbsp;' * indent, numer + str(i), label.lstrip('0123456789. '), page_num_td_style, page + 1))
                _printSummary(children, indent + 2, numer + str(i) + '.')
        _printSummary(content.make_bookmark_tree())

        #Priting summary table END
        self.summary += '</table>'

        homepage = HTML(string=self.homepage, encoding="utf-8").render(stylesheets=[self.homepage_css])
        summary = HTML(string=self.summary, encoding="utf-8").render(stylesheets=[self.homepage_css])

        pdf_report = [homepage, summary, content]
        logging.getLogger().warning(pdf_report[2].make_bookmark_tree())

        all_pages = [doc.pages for doc in pdf_report]

        # Second step, clean sublist and make a simple list
        # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
        all_pages = [item for sublist in all_pages for item in sublist]

        # ...And combine these pages into a single report Document
        pdf_report[0].copy(all_pages).write_pdf(self.path)

        chmod(self.path, 0644)
        return self.path


class SVGGenerator(object):
    def __init__(self, path='/tmp/graph.png', locale={}, extra_css=[]):
        self.style = None
        self.chart = None
        self.path = path
        self.locale = locale
        self.config = Config()
        self.config.no_data_text = 'No result found'
        self.config.no_data_font_size = 13
        self.config.x_label_rotation = 45
        for css in extra_css:
            self.config.css.append(css)
        if 'STR_NODATA' in self.locale:
            self.config.no_data_text = self.locale['STR_NODATA']

    def _get_style(self):
        colors = ('#fce94f', '#8ae234', '#fcaf3e', '#729fcf', '#e9b96e', '#ad7fa8', '#ef2929',
                  '#edd400', '#73d216', '#f57900', '#3465a4', '#c17d11', '#75507b', '#cc0000')
        colors = ('#87CEEB', '#32CD32', '#BA55D3', '#F08080', '#4682B4', '#9ACD32', '#40E0D0',
                  '#FF69B4', '#F0E68C', '#D2B48C', '#8FBC8B', '#6495ED', '#DDA0DD', '#5F9EA0',
                  '#FFDAB9', '#FFA07A')
        return Style(
            background='#fff',
            plot_background='#f7f7f7',
            foreground='#333',
            foreground_light='#555',
            foreground_dark='#111',
            opacity='1',
            opacity_hover='1',
            transition='500ms ease-in',
            colors=colors)

    def _get_bar_chart(self):
        return pygal.StackedBar(
            self.config,
            style=self._get_style(),
            no_data_text=self.config.no_data_text,
            disable_xml_declaration=True,   # for correct svg in web page
            explicit_size=True,
            show_dots=False
        )

    def _get_line_chart(self):
        return pygal.Line(
            self.config,
            style=self._get_style(),
            disable_xml_declaration=True,   # for correct svg in web page
            explicit_size=True,
            show_dots=False,
        )

    def _get_pie_chart(self):
        return pygal.Pie(
            self.config,
            style=self._get_style(),
            no_data_text=self.config.no_data_text,
            disable_xml_declaration=True,   # for correct svg in web page
            explicit_size=True,
            show_dots=False
        )

    def _filterDatas(self, datas):
        """
        Remove items where all values are 0 or None for all periods
        """
        values_idx = range(0, len(datas['titles']))
        values_idx.reverse()
        periods_idx = range(0, len(datas['dates']))
        periods_idx.reverse()
        for value_idx in values_idx:
            remove = True
            for period_idx in periods_idx:
                if datas['values'][period_idx][value_idx] is not None and \
                        datas['values'][period_idx][value_idx] > 0:
                    remove = False
                    break
            if remove:
                del datas['titles'][value_idx]
                for period in datas['values']:
                    del period[value_idx]
        return datas

    def _feedChart(self, title, datas, type='period'):
        if type == 'period':
            datas = self._filterDatas(datas)
        self.chart.title = title
        if type == 'period':
            titles = datas['titles']
            values = datas['values']
            self.chart.x_labels = datas['dates']
            for i in xrange(len(titles)):
                self.chart.add(titles[i], [x[i] for x in values])
        elif type == 'key_value':   # Pie Chart
            titles = datas['headers']
            values = datas['values']
            for x in xrange(len(values)):
                self.chart.add(values[x][0], values[x][1])
        return True

    def barChart(self, title, datas):
        self.chart = self._get_bar_chart()
        self._feedChart(title, datas)

    def lineChart(self, title, datas):
        self.chart = self._get_line_chart()
        self._feedChart(title, datas)

    def pieChart(self, title, datas):
        self.chart = self._get_pie_chart()
        self._feedChart(title, datas, type='key_value')

    def toXML(self):
        self.chart.config.width = 500
        self.chart.config.height = 280
        self.chart.config.legend_font_size = 11
        self.chart.config.label_font_size = 11
        self.chart.config.major_label_font_size = 11
        self.chart.config.value_font_size = 10
        self.chart.config.tooltip_font_size = 10
        self.chart.config.title_font_size = 13
        return self.chart.render()

    def toPNG(self):
        self.chart.config.width = 800
        self.chart.config.height = 600

        self.chart.config.legend_font_size = 11
        self.chart.config.label_font_size = 11
        self.chart.config.major_label_font_size = 11
        self.chart.config.value_font_size = 10
        self.chart.config.title_font_size = 16

        self.chart.render_to_png(self.path + '.png')
        chmod(self.path + '.png', 0644)
        return True

    def save(self):
        # Saving PNG file
        self.toPNG()
        # Saving SVG file
        f = open(self.path + '.svg', 'w')
        f.write(self.toXML().encode('utf8'))
        f.close()
        chmod(self.path + '.svg', 0644)
        return True
