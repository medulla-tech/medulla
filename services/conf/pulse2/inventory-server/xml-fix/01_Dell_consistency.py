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
                for subelem3 in subelem2:
                    # DELL vendor name should allways be the same
                    if subelem3.text in [
                        "DELL",
                        "Dell Corp.",
                        "Dell Computer Corp.",
                        "Dell",
                        "Dell Computer Corporation",
                    ]:
                        subelem3.text = "Dell Inc."

    return ET.tostring(root)
