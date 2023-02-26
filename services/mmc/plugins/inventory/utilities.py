# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Contains some utilities methods.
"""

def getInventoryParts():
    """
    @return: Return all available inventory parts
    @rtype: list
    """
    return [ "Bios", "BootDisk", "BootGeneral", "BootMem", "BootPart", "BootPCI", "Controller", "Custom", "Drive", "Hardware", "Input", "Memory", "Modem", "Monitor", "Network", "Port", "Printer", "Slot", "Software", "Sound", "Storage", "VideoCard", "Registry", "Entity" ]


def getInventoryNoms(table = None):
    """
    @return: Return all available nomenclatures tables
    @rtype: dict
    """
    noms = {
        'Registry':['Path']
    }

    if table == None:
        return noms
    if table in noms:
        return noms[table]
    return None
