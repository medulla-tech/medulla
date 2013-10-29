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

import pygal
from os import chmod
from pygal.style import Style
from datetime import datetime
from base64 import b64encode

from mmc.plugins.report.database import ReportDatabase

class Monitoring(object):
    def get_disc_space(self, *args, **kargs):
        """
        Get datas of disc space report for a given period
        period is splited into several parts

        @param from_timestamp: timestamp of starting period
        @type from_timestamp: int
        @param to_timestamp: timestamp of ending period
        @type to_timestamp: int
        @param splitter: period will be splitted
        @type splitter: int

        @return: list of datas for period, list number is equal to splitter param
        @rtype: list
        """
        from_timestamp = datetime.fromtimestamp(int(args[0]))
        to_timestamp = datetime.fromtimestamp(int(args[1]))
        splitter = int(args[2])
        db = ReportDatabase()
        return db.getDiscSpace(from_timestamp, to_timestamp, splitter)

    def get_disc_space_pdf(self, *args, **kargs):
        def timestamp_to_date(timestamp):
            return datetime.fromtimestamp(int(timestamp)).strftime('%Y/%m/%d')

        title = kargs['title']
        html = kargs['html']
        html += '<h1>%s</h1>' % title

        r = self.get_disc_space(*args, **kargs)

        titles = r.pop('titles', None)
        # get r keys and order them
        headers = r.keys()
        headers.sort()

        # Table
        html += '<table>'
        html += '<tr>'
        html += '<th>'
        html += '</th>'
        for h in headers:
            html += '<th>'
            html += timestamp_to_date(h)
            html += '</th>'
        for x in xrange(len(titles)):
            html += '<tr>'

            html += '<td>'
            html += titles[x]
            html += '</td>'
            for y in headers:
                html += '<td>'
                html += str(r[y][x])
                html += '</td>'

            html += '</tr>'

        html += '</tr>'
        html += '</table>'

        # SVG
        svg = self.get_disc_space_svg(*args, **kargs)
        svg = svg.encode('utf8')
        html += '<img src="data:image/svg+xml;charset=utf-8;base64,%s" />' % b64encode(svg)

        return html

    def get_disc_space_svg(self, *args, **kargs):
        """
        return Disc Space SVG
        """
        def timestamp_to_date(timestamp):
            return datetime.fromtimestamp(int(timestamp)).strftime('%Y/%m/%d')

        custom_style = Style(
            background='transparent',
            plot_background='transparent',
            foreground='#000',
            foreground_light='#000',
            foreground_dark='#000',
            colors=('red', 'blue'),
        )

        line_chart = pygal.StackedBar(
            style=custom_style,
            x_label_rotation=90,
            disable_xml_declaration=True, # for correct svg in web page
            explicit_size=True,
            show_dots=False,
            width=500,
            height=250
        )

        datas = self.get_disc_space(*args, **kargs)
        #line_chart.title = 'Disc Space'
        titles = datas.pop('titles', None)
        labels = datas.keys()
        labels.sort()

        line_chart.x_labels = [timestamp_to_date(x) for x in labels]
        for i in xrange(len(titles)):
            line_chart.add(titles[i], [datas[x][i] for x in labels])

        if 'render' in kargs:
            filepath = '/tmp/graph.png'
            line_chart.render_to_png(filepath)
            chmod(filepath, 0644)
            return filepath
        return line_chart.render()

    def get_ram_usage(self, *args, **kargs):
        """
        Get datas of disc space report for a given period
        period is splited into several parts

        @param from_timestamp: timestamp of starting period
        @type from_timestamp: int
        @param to_timestamp: timestamp of ending period
        @type to_timestamp: int
        @param splitter: period will be splitted
        @type splitter: int

        @return: list of datas for period, list number is equal to splitter param
        @rtype: list
        """
        from_timestamp = datetime.fromtimestamp(int(args[0]))
        to_timestamp = datetime.fromtimestamp(int(args[1]))
        splitter = int(args[2])
        db = ReportDatabase()
        return db.getRamUsage(from_timestamp, to_timestamp, splitter)

    def get_ram_usage_pdf(self, *args, **kargs):
        def timestamp_to_date(timestamp):
            return datetime.fromtimestamp(int(timestamp)).strftime('%Y/%m/%d')

        title = kargs['title']
        html = kargs['html']
        html += '<h1>%s</h1>' % title

        r = self.get_ram_usage(*args, **kargs)

        titles = r.pop('titles', None)
        # get r keys and order them
        headers = r.keys()
        headers.sort()

        # Table
        html += '<table>'
        html += '<tr>'
        html += '<th>'
        html += '</th>'
        for h in headers:
            html += '<th>'
            html += timestamp_to_date(h)
            html += '</th>'
        for x in xrange(len(titles)):
            html += '<tr>'

            html += '<td>'
            html += titles[x]
            html += '</td>'
            for y in headers:
                html += '<td>'
                html += str(r[y][x])
                html += '</td>'

            html += '</tr>'

        html += '</tr>'
        html += '</table>'

        return html
