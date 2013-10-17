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
from datetime import datetime, timedelta
from base64 import b64encode

from mmc.plugins.backuppc.database import ReportDatabase
from mmc.plugins.backuppc import bpc
from mmc.plugins.base.computers import ComputerManager

class Backuppc(object):
    def get_backuppc_server_disc_space(self, *args, **kargs):
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
        entities = [int(str(x).replace('UUID', '')) for x in [kargs['entities']]]
        db = ReportDatabase()
        return db.get_backuppc_server_disc_space(from_timestamp, to_timestamp, splitter, entities)

    def get_backuppc_server_disc_space_xls(self, *args, **kargs):
        def timestamp_to_date(timestamp):
            return datetime.fromtimestamp(int(timestamp)).strftime('%Y/%m/%d')

        title = kargs['title']
        wbk = kargs['wbk']
        res = self.get_backuppc_server_disc_space(*args, **kargs)
        for x in res:
            r = res[x]
            sheet = wbk.add_sheet(title)
            line = 0
            column = 0
            sheet.write(line, column, '')
            for i in xrange(len(r['titles'])):
                line += 1
                sheet.write(line, column, r['titles'][i])
            r.pop('titles', None)

            # get r keys and order them
            headers = r.keys()
            headers.sort()
            for i in xrange(len(headers)):
                column += 1
                line = 0
                sheet.write(line, column, timestamp_to_date(headers[i]))
                for j in xrange(len(r[headers[i]])):
                    line += 1
                    sheet.write(line, column, r[headers[i]][j])
        return wbk

    def get_backuppc_server_disc_space_pdf(self, *args, **kargs):
        def timestamp_to_date(timestamp):
            return datetime.fromtimestamp(int(timestamp)).strftime('%Y/%m/%d')

        title = kargs['title']
        html = kargs['html']
        html += '<h1>%s</h1>' % title

        res = self.get_backuppc_server_disc_space(*args, **kargs)

        for x in res:
            r = res[x]
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
            svg = self.get_backuppc_server_disc_space_svg(*args, **kargs)
            svg = svg.encode('utf8')
            html += '<img src="data:image/svg+xml;charset=utf-8;base64,%s" />' % b64encode(svg)

        return html

    def get_backuppc_server_disc_space_svg(self, *args, **kargs):
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

        datas = self.get_backuppc_server_disc_space(*args, **kargs)
        datas = datas[str(kargs['entities']).replace('UUID', '')]
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

    def get_backuppc_used_disc_space_per_machine(self, *args, **kargs):
        from_timestamp = datetime.fromtimestamp(int(args[0]))
        to_timestamp = datetime.fromtimestamp(int(args[1]))
        splitter = int(args[2])
        entities = [int(str(x).replace('UUID', '')) for x in [kargs['entities']]]
        db = ReportDatabase()
        return db.get_backuppc_used_disc_space_per_machine(from_timestamp, to_timestamp, splitter, entities, kargs)

    def get_backuppc_used_disc_space_per_machine_xls(self, *args, **kargs):
        def timestamp_to_date(timestamp):
            return datetime.fromtimestamp(int(timestamp)).strftime('%Y/%m/%d')

        title = kargs['title']
        wbk = kargs['wbk']
        res = self.get_backuppc_used_disc_space_per_machine(*args, **kargs)
        for x in res:
            r = res[x]
            sheet = wbk.add_sheet(title)
            line = 0
            column = 0
            sheet.write(line, column, '')
            for i in xrange(len(r['titles'])):
                line += 1
                sheet.write(line, column, r['titles'][i])
            r.pop('titles', None)

            # get r keys and order them
            headers = r.keys()
            headers.sort()
            for i in xrange(len(headers)):
                column += 1
                line = 0
                sheet.write(line, column, timestamp_to_date(headers[i]))
                for j in xrange(len(r[headers[i]])):
                    line += 1
                    sheet.write(line, column, r[headers[i]][j])
        return wbk

    def get_backuppc_used_disc_space_per_machine_pdf(self, *args, **kargs):
        def timestamp_to_date(timestamp):
            return datetime.fromtimestamp(int(timestamp)).strftime('%Y/%m/%d')

        title = kargs['title']
        html = kargs['html']
        html += '<h1>%s</h1>' % title

        res = self.get_backuppc_used_disc_space_per_machine(*args, **kargs)

        for x in res:
            r = res[x]
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
            svg = self.get_backuppc_used_disc_space_per_machine_svg(*args, **kargs)
            svg = svg.encode('utf8')
            html += '<img src="data:image/svg+xml;charset=utf-8;base64,%s" />' % b64encode(svg)

        return html

    def get_backuppc_used_disc_space_per_machine_svg(self, *args, **kargs):
        def timestamp_to_date(timestamp):
            return datetime.fromtimestamp(int(timestamp)).strftime('%Y/%m/%d')

        custom_style = Style(
            background='#444',
        )

        line_chart = pygal.Line(
            style=custom_style,
            x_label_rotation=90,
            disable_xml_declaration=True, # for correct svg in web page
            explicit_size=True,
            #show_dots=False,
            width=500,
            height=250
        )

        datas = self.get_backuppc_used_disc_space_per_machine(*args, **kargs)
        datas = datas[str(kargs['entities']).replace('UUID', '')]
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

    def get_backuppc_last_backup_date(self, *args, **kargs):
        entities = [int(str(x).replace('UUID', '')) for x in [kargs['entities']]]

        def get_computer_hostname(uuid, computers_list):
            if uuid in computers_list:
                return computers_list[uuid][1]['cn'][0]
            else:
                return uuid
        def get_last_backup_timestamp(last_backup):
            now = datetime.now()
            delta = timedelta(float(last_backup))
            return (now - delta).strftime('%s')

        ret = {}
        for entity in entities:
            status = bpc.get_global_status('UUID' + str(entity))
            hosts = status['data']['hosts']
            last_backup = status['data']['last_backup']
            computers_list = ComputerManager().getComputersList({'uuids': [uuid.upper() for uuid in hosts if uuid != 'localhost']})
            ret[str(entity)] = {
                'hosts': [get_computer_hostname(uuid.upper(), computers_list) for uuid in hosts],
                'last_backup': [get_last_backup_timestamp(x) for x in last_backup],
            }
        return ret

    def get_backuppc_last_backup_date_xls(self, *args, **kargs):
        pass

    def get_backuppc_last_backup_date_pdf(self, *args, **kargs):
        pass
