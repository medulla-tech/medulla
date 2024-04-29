# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later


def xml_fix(xml):
    import xml.etree.cElementTree as ET
    import re

    xml = ET.fromstring(xml)
    tree = ET.ElementTree(xml)
    root = tree.getroot()
    for subelem1 in root:
        if subelem1.tag == "CONTENT":
            for subelem2 in subelem1:
                # Apply for anything, not softwares only
                for subelem3 in subelem2:
                    # Microsoft vendor name should allways be the same
                    if subelem3.text in ["Microsoft", "MICROSOFT", "MicrosoftH"]:
                        subelem3.text = "Microsoft Corporation"

                if subelem2.tag == "SOFTWARES":
                    for subelem3 in subelem2:
                        if subelem3.tag == "NAME":
                            # Convert Microsoft KB updates
                            #  from: {CE2CDD62-0124-36CA-84D3-9F4DCF5C5BD9}.KB960043
                            #  to: Update (KB960043)
                            # Also handle KB1234v5 or KB1234-v5 naming scheme
                            if re.match(
                                "^\{[\dA-Fa-f]{8}-[\dA-Fa-f]{4}-[\dA-Fa-f]{4}-[\dA-Fa-f]{4}-[\dA-Fa-f]{12}\}\.KB[0-9]+(-?v[0-9]+)?$",
                                subelem3.text,
                            ):
                                subelem3.text = re.sub(
                                    "\{[\dA-Fa-f]{8}-[\dA-Fa-f]{4}-[\dA-Fa-f]{4}-[\dA-Fa-f]{4}-[\dA-Fa-f]{12}\}\.",
                                    "Update (",
                                    subelem3.text,
                                )
                                subelem3.text = re.sub("$", ")", subelem3.text)

                            # Convert Microsoft KB updates
                            #  from: KB960043
                            #  to: Update (KB960043)
                            # Also handle KB1234v5 or KB1234-v5 naming scheme
                            if re.match("^KB[0-9]+(-?v[0-9]+)?$", subelem3.text):
                                subelem3.text = re.sub("^", "Update (", subelem3.text)
                                subelem3.text = re.sub("$", ")", subelem3.text)

                            # Contains KB1234v5 or KB123467 in its name without any publisher ?
                            # Publisher set to Microsoft Corporation
                            if re.search(
                                "KB[0-9]+(v[0-9]+)?", subelem3.text
                            ) and not subelem2.findall("PUBLISHER"):
                                children = ET.SubElement(subelem2, "PUBLISHER")
                                children.text = "Microsoft Corporation"

                            # FusionInventory on Windows XP report some weird things we'll drop
                            if subelem3.text in [
                                "ie7",
                                "Branding",
                                "IDNMitigationAPIs",
                                "NLSDownlevelMapping",
                                "PCHealth",
                            ] and not subelem2.findall("PUBLISHER"):
                                subelem1.remove(subelem2)

                            # Windows Media and .NET framework stuff needs Microsoft vendor too
                            if re.search(
                                "(Windows Media|Microsoft .NET Framework)",
                                subelem3.text,
                            ) and not subelem2.findall("PUBLISHER"):
                                children = ET.SubElement(subelem2, "PUBLISHER")
                                children.text = "Microsoft Corporation"

                            # French to english
                            if re.search("Mise à jour de sécurité pour", subelem3.text):
                                subelem3.text = re.sub(
                                    "Mise à jour de sécurité pour",
                                    "Security Update for",
                                    subelem3.text,
                                )
                            if re.search("Mise à jour pour", subelem3.text):
                                subelem3.text = re.sub(
                                    "Mise à jour pour", "Update for", subelem3.text
                                )
                            if re.search("Correctif pour", subelem3.text):
                                subelem3.text = re.sub(
                                    "Correctif pour", "Update for", subelem3.text
                                )
                            if re.search("Lecteur Windows Media", subelem3.text):
                                subelem3.text = re.sub(
                                    "Lecteur Windows Media",
                                    "Windows Media Player",
                                    subelem3.text,
                                )

                # There's an entry for the OS itself but without any publisher
                # Doesn't seem to work with GLPI sadly
                if subelem2.tag == "OPERATINGSYSTEM":
                    for subelem3 in subelem2:
                        if subelem3.tag == "FULL_NAME":
                            if re.search(
                                "^Microsoft Windows (2000|2003|XP|Vista|7|8) ",
                                subelem3.text,
                            ) and not subelem2.findall("PUBLISHER"):
                                children = ET.SubElement(subelem2, "PUBLISHER")
                                children.text = "Microsoft Corporation"

    return ET.tostring(root)
