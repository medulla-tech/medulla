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
                if subelem2.tag == "SOFTWARES":
                    for subelem3 in subelem2:
                        if subelem3.tag == "NAME":
                            # Is ATI Catalyst Control Center or ATI Display Driver without any publisher ?
                            # Publisher set to ATI
                            if subelem3.text in [
                                "ATI Catalyst Control Center",
                                "ATI Display Driver",
                            ] and not subelem2.findall("PUBLISHER"):
                                children = ET.SubElement(subelem2, "PUBLISHER")
                                children.text = "ATI"

    return ET.tostring(root)
