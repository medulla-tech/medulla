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

import xlwt
from os import chmod

from mmc.plugins.report.utils import timestamp_to_date

class XlsGenerator(object):
    def __init__(self, path = '/tmp/report.xls'):
        self.wbk = xlwt.Workbook()
        self.path = path

    def get_xls_sheet(self, datas, *args, **kargs):
        title = kargs['title']
        sheet = self.wbk.add_sheet(title)
        line = 0
        column = 0
        sheet.write(line, column, '')
        for i in xrange(len(datas['titles'])):
            line += 1
            sheet.write(line, column, datas['titles'][i])
        datas.pop('titles', None)

        # get r keys and order them
        headers = datas.keys()
        headers.sort()
        for i in xrange(len(headers)):
            column += 1
            line = 0
            sheet.write(line, column, timestamp_to_date(headers[i]))
            for j in xrange(len(datas[headers[i]])):
                line += 1
                sheet.write(line, column, datas[headers[i]][j])
        return self.wbk

    def save(self):
        self.wbk.save(self.path)
        chmod(self.path, 0644)
        return self.path
