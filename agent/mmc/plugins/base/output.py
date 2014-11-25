# -*- coding: utf-8; -*-
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
This module generate XLS output files
"""

import os
from os import chmod
import xlwt

class XLSGenerator(object):
    def __init__(self, path='/tmp/report.xls'):
        self.wbk = xlwt.Workbook(encoding='utf-8')
        self.path = path

    def get_summary_sheet(self,datas):
        sheet = self.wbk.add_sheet('Summary')
        self.create_summary_table(sheet,0,0,"",datas)

    def get_hardware_sheet(self,processors_data,controllers_data,
        graphic_card_data,sound_card_data):
        sheet = self.wbk.add_sheet('Hardware')
        line = 0
        if processors_data:
            line = self.create_simple_table(sheet,line,0,"Processors",processors_data)
        if controllers_data:
            line = self.create_simple_table(sheet,line,0,"Controllers",controllers_data)
        if graphic_card_data:
            line = self.create_simple_table(sheet,line,0,"GraphicCards",graphic_card_data)
        if sound_card_data:
            line = self.create_simple_table(sheet,line,0,"SoundCards",sound_card_data)

    def get_storage_sheet(self,datas):
        sheet = self.wbk.add_sheet('Storage')
        if datas:
            self.create_simple_table(sheet,0,0,"Storage",datas)

    def get_software_sheet(self,datas):
        sheet = self.wbk.add_sheet('Software')
        if datas:
            self.create_simple_table(sheet,0,0,"Software",datas)

    def get_network_sheet(self,datas):
        sheet = self.wbk.add_sheet('Network')
        if datas:
            self.create_simple_table(sheet,0,0,"Network",datas)

    def create_summary_table(self,sheet,line,column,table_name, datas):
        if table_name:
            sheet.write(line,column,table_name)
            line +=1
        for section in datas:
            for row in section:
                for cell in row:
                    try:
                        if isinstance (cell,basestring):
                            sheet.write(line,column,cell)
                        else:
                            if isinstance (cell[2],basestring):
                                sheet.write(line,column,cell[2])
                    except Exception:
                        pass
                    column += 1
                column = 0
                line += 1
            line += 2
        return line

    def save(self):
        self.wbk.save(self.path)
        chmod(self.path, 0644)
        return self.path

    def create_simple_table(self,sheet,line,column,table_name, datas):
        if table_name:
            sheet.write(line,column,table_name)
            line += 1
        #write headers
        headers=[]
        for section in datas:
            for elements in section :
                try:
                    if isinstance (elements[0],basestring):
                        if elements[0] not in headers:
                            headers.append(elements[0])
                            sheet.write(line,column,elements[0])
                        column += 1
                except Exception:
                    pass
        line += 1
        #write data
        for section in datas:
            for elements in section :
                try:
                    if isinstance (elements[0],basestring) and isinstance (elements[1],basestring):
                        sheet.write(line,headers.index(elements[0]),elements[1])
                except Exception:
                    pass
                column += 1
            line += 1
        line += 1
        return line
