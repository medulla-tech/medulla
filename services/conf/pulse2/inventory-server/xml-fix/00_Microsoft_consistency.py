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
  import re
  xml = ET.fromstring(xml)
  tree = ET.ElementTree(xml)
  root = tree.getroot()
  for subelem1 in root:
    if subelem1.tag == 'CONTENT':
      for subelem2 in subelem1:
        if subelem2.tag == 'SOFTWARES':
          for subelem3 in subelem2:
            
            if subelem3.tag == 'PUBLISHER':

              # Microsoft vendor name should allways be the same
              if subelem3.text in ['Microsoft', 'MICROSOFT']:
                subelem3.text = 'Microsoft Corporation'

            if subelem3.tag == 'NAME':
             
              # Convert Microsoft KB updates
              #  from: {CE2CDD62-0124-36CA-84D3-9F4DCF5C5BD9}.KB960043
              #  to: Update (KB960043)
              # Also handle KB1234v5 or KB1234-v5 naming scheme
              if re.match('^\{[\dA-Fa-f]{8}-[\dA-Fa-f]{4}-[\dA-Fa-f]{4}-[\dA-Fa-f]{4}-[\dA-Fa-f]{12}\}\.KB[0-9]+(-?v[0-9]+)?$',subelem3.text):
                subelem3.text = re.sub('\{[\dA-Fa-f]{8}-[\dA-Fa-f]{4}-[\dA-Fa-f]{4}-[\dA-Fa-f]{4}-[\dA-Fa-f]{12}\}\.','Update (',subelem3.text)
                subelem3.text = re.sub('$',')',subelem3.text)

              # Convert Microsoft KB updates
              #  from: KB960043
              #  to: Update (KB960043)
              # Also handle KB1234v5 or KB1234-v5 naming scheme
              if re.match('^KB[0-9]+(-?v[0-9]+)?$',subelem3.text):
                subelem3.text = re.sub('^','Update (',subelem3.text)
                subelem3.text = re.sub('$',')',subelem3.text)

              # Contains KB1234v5 or KB123467 in its name without any publisher ?
              # Publisher set to Microsoft Corporation
              if re.search('KB[0-9]+(v[0-9]+)?',subelem3.text) and not subelem2.findall('PUBLISHER'):
                children = ET.SubElement(subelem2,'PUBLISHER')
                children.text = 'Microsoft Corporation'

              # Windows Media and .NET framework stuff needs Microsoft vendor too
              if re.search('(Windows Media|Microsoft .NET Framework)',subelem3.text) and not subelem2.findall('PUBLISHER'):
                children = ET.SubElement(subelem2,'PUBLISHER')
                children.text = 'Microsoft Corporation'

              # French to english
              if re.search(u'Mise à jour de sécurité pour',subelem3.text):
                subelem3.text = re.sub(u'Mise à jour de sécurité pour','Security Update for',subelem3.text)
              if re.search(u'Mise à jour pour',subelem3.text):
                subelem3.text = re.sub(u'Mise à jour pour','Update for',subelem3.text)
              if re.search('Correctif pour',subelem3.text):
                subelem3.text = re.sub('Correctif pour','Update for',subelem3.text)
              if re.search('Lecteur Windows Media',subelem3.text):
                subelem3.text = re.sub('Lecteur Windows Media','Windows Media Player',subelem3.text)

  return ET.tostring(root)
