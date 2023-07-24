# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later


def xml_fix(xml):
    import xml.etree.cElementTree as ET

    xml = ET.fromstring(xml)
    tree = ET.ElementTree(xml)
    root = tree.getroot()
    for subelem1 in root:
        if subelem1.tag == "CONTENT":
            for subelem2 in subelem1:
                if subelem2.tag == "BIOS":
                    for subelem3 in subelem2:
                        if subelem3.tag == "TYPE":
                            if subelem3.text in ["Notebook", "Portable"]:
                                subelem3.text = "Laptop"

    return ET.tostring(root)
