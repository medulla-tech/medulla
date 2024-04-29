# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# Just to make stdout work when testing from command line
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
# f = open('inventorylog-pre-1394533661.xml', 'r').read()


def xml_fix(xml):
    import xml.etree.cElementTree as ET

    xml = ET.fromstring(xml)
    tree = ET.ElementTree(xml)
    root = tree.getroot()
    for elem in root.iter():
        # Only existing entries without childs
        if not list(elem) and elem.text:
            elem.text = elem.text.strip()
    return ET.tostring(root)
