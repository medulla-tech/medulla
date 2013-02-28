# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Mandriva S.A, http://www.mandriva.com
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


def xml_fix(xml):
  import xml.etree.cElementTree as ET
  xml = ET.fromstring(xml)
  tree = ET.ElementTree(xml)
  root = tree.getroot()
  for subelem1 in root:
    if subelem1.tag == 'CONTENT':
      for subelem2 in subelem1:
          
        if subelem2.tag == 'SOFTWARES':
          for subelem3 in subelem2:
            
            if subelem3.tag == 'NAME':
             
              # Is ATI Catalyst Control Center or ATI Display Driver without any publisher ?
              # Publisher set to ATI
              if subelem3.text in ['ATI Catalyst Control Center', 'ATI Display Driver'] and not subelem2.findall('PUBLISHER'):
                children = ET.SubElement(subelem2,'PUBLISHER')
                children.text = 'ATI'

  return ET.tostring(root)
