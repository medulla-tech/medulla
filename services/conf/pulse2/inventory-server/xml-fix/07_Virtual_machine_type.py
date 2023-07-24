# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later


def xml_fix(xml):
    import xml.etree.cElementTree as ET

    xml = ET.fromstring(xml)
    tree = ET.ElementTree(xml)
    root = tree.getroot()
    is_bochs = 0
    is_vbox = 0

    # Let's try to figure out if it looks like being a KVM using Bochs emulated BIOS
    for subelem1 in root:
        if subelem1.tag == "CONTENT":
            for subelem2 in subelem1:
                if subelem2.tag == "BIOS":
                    for subelem3 in subelem2:
                        if subelem3.tag in [
                            "BMANUFACTURER",
                            "BVERSION",
                            "SMANUFACTURER",
                            "SMODEL",
                        ]:
                            if subelem3.text == "Bochs":
                                is_bochs += 1
    # Or Vbox
    for subelem1 in root:
        if subelem1.tag == "CONTENT":
            for subelem2 in subelem1:
                if subelem2.tag == "BIOS":
                    for subelem3 in subelem2:
                        if (
                            subelem3.tag in ["BMANUFACTURER", "SMANUFACTURER"]
                            and subelem3.text == "innotek GmbH"
                            or subelem3.tag not in ["BMANUFACTURER", "SMANUFACTURER"]
                            and subelem3.tag in ["BVERSION", "SMODEL"]
                            and subelem3.text == "VirtualBox"
                        ):
                            is_vbox += 1
    # Fix chassis type
    if is_bochs == 4 or is_vbox == 4:
        for subelem1 in root:
            if subelem1.tag == "CONTENT":
                for subelem2 in subelem1:
                    if subelem2.tag == "HARDWARE":
                        for subelem3 in subelem2:
                            if subelem3.tag == "CHASSIS_TYPE":
                                subelem3.text = "Virtual Machine"
                    if subelem2.tag == "BIOS":
                        for subelem3 in subelem2:
                            if subelem3.tag == "TYPE":
                                subelem3.text = "Virtual Machine"

    return ET.tostring(root)
