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

import xlwt
from weasyprint import HTML, CSS
import pygal
from pygal.style import Style
from os import chmod
from base64 import b64encode

class XlsGenerator(object):
    def __init__(self, path = '/tmp/report.xls'):
        self.wbk = xlwt.Workbook()
        self.path = path

    def pushTable(self, title, datas):
        if 'headers' in datas: # simple sheets
            return self.get_simple_sheet(title, datas)
        else: # period sheets
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

class PdfGenerator(object):
    def __init__(self, path = '/tmp/report.pdf'):
        self.front = self.get_front_page()
        self.summary = self.get_summary_page()
        self.css = self.get_css()
        self.html = ''
        self.path = path

    def h1(self, str):
        return '<h1>%s</h1>' % str

    def h2(self, str):
        return '<h2>%s</h2>' % str

    def h3(self, str):
        return '<h3>%s</h3>' % str

    def get_front_page(self):
        return HTML(string='<h1>Report</h1>').render()

    def get_summary_page(self):
        return HTML(string='<p>Summary</p>').render()

    def get_css(self):
        string = """
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
        return CSS(string=string)

    def get_simple_sheet(self, title, datas):
        self.html += self.h3(title)

        headers = datas['headers']
        values = datas['values']

        # Table headers
        self.html += '<table>'
        self.html += '<tr>'
        for h in headers:
            if h == 'titles' : continue
            self.html += '<th>'
            self.html += h
            self.html += '</th>'
        self.html += '</tr>'

        # Table content
        for line in values:
            self.html += '<tr>'
            for td in line:
                if isinstance(td, (int, float)): td = str(td)
                self.html += '<td>'
                self.html += td
                self.html += '</td>'
            self.html += '</tr>'

        self.html += '</table>'

    def get_period_sheet(self, title, datas):
        self.html += self.h3(title)
        titles = datas['titles']
        dates = datas['dates']
        values = datas['values']

        # Table
        self.html += '<table>'
        self.html += '<tr>'
        self.html += '<th>'
        self.html += '</th>'
        for d in dates:
            self.html += '<th>'
            self.html += d
            self.html += '</th>'
        for x in xrange(len(titles)):
            self.html += '<tr>'

            self.html += '<td>'
            self.html += titles[x]
            self.html += '</td>'
            for v in values:
                if v[x] is None:
                    v[x] = ''
                elif isinstance(v[x], (int, float)):
                    v[x] = str(v[x])
                self.html += '<td>'
                self.html += v[x]
                self.html += '</td>'

            self.html += '</tr>'

        self.html += '</tr>'
        self.html += '</table>'

    def pushTable(self, title, datas):
        if 'headers' in datas: # simple sheets
            return self.get_simple_sheet(title, datas)
        else: # period sheets
            return self.get_period_sheet(title, datas)

    def pushSVG(self, svg):
        self.html += '<img src="data:image/svg+xml;charset=utf-8;base64,%s" />' % b64encode(svg.encode('utf8'))

    def save(self):
        content = HTML(string=self.html).render(stylesheets=[self.css])
        # PDF report is a list of all documents
        pdf_report = [self.front, self.summary, content]

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
        pdf_report[0].copy(all_pages).write_pdf(self.path)

        chmod(self.path, 0644)
        return self.path

class SvgGenerator(object):
    def __init__(self, path = '/tmp/graph.png'):
        self.style = None
        self.chart = None
        self.path = path

    def _get_bar_style(self):
        return Style(
            background='transparent',
            plot_background='transparent',
            foreground='#000',
            foreground_light='#000',
            foreground_dark='#000',
            colors=('red', 'blue'),
        )

    def _get_bar_chart(self):
        return pygal.StackedBar(
            style=self.style,
            x_label_rotation=90,
            disable_xml_declaration=True, # for correct svg in web page
            explicit_size=True,
            show_dots=False,
            width=500,
            height=250
        )

    def _get_line_style(self):
        return Style(
            background='transparent',
            plot_background='transparent',
            foreground='#000',
            foreground_light='#000',
            foreground_dark='#000',
            colors=('red', 'blue'),
        )

    def _get_line_chart(self):
        return pygal.Line(
            style=self.style,
            x_label_rotation=90,
            disable_xml_declaration=True, # for correct svg in web page
            explicit_size=True,
            show_dots=False,
            width=500,
            height=250
        )

    def _get_pie_style(self):
        return Style(
            background='transparent',
            plot_background='transparent',
            foreground='#000',
            foreground_light='#000',
            foreground_dark='#000',
            colors=('red', 'blue'),
        )

    def _get_pie_chart(self):
        return pygal.Pie(
            style=self.style,
            x_label_rotation=90,
            disable_xml_declaration=True, # for correct svg in web page
            explicit_size=True,
            show_dots=False,
            width=500,
            height=250
        )

    def _feedChart(self, title, datas, type='period'):
        self.chart.title = title
        if type == 'period':
            titles = datas['titles']
            values = datas['values']

            self.chart.x_labels = datas['dates']
            for i in xrange(len(titles)):
                self.chart.add(titles[i], values[i])
        elif type == 'key_value': # Pie Chart
            titles = datas['headers']
            values = datas['values']
            for x in xrange(len(values)):
                self.chart.add(values[x][0], values[x][1])

        return True

    def barChart(self, title, datas):
        self.style = self._get_bar_style()
        self.chart = self._get_bar_chart()
        self._feedChart(title, datas)

    def lineChart(self, title, datas):
        self.style = self._get_line_style()
        self.chart = self._get_line_chart()
        self._feedChart(title, datas)

    def pieChart(self, title, datas):
        self.style = self._get_pie_style()
        self.chart = self._get_pie_chart()
        self._feedChart(title, datas, type='key_value')

    def toXML(self):
        return self.chart.render()

    def toPNG(self):
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
