# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Imaging API XML-RPC client to connect to the MMC agent.
"""

from pulse2.apis.clients import Pulse2Api

class ImagingXMLRPCClient(Pulse2Api):

    """
    Imaging API XML-RPC client to connect to the MMC agent.
    """

    name = "ImagingXMLRPCClient"
