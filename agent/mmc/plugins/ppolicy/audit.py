# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Constants for the audit framework and the ppolicy plugin.
"""

from mmc.plugins.base.audit import AT

PLUGIN_NAME = "MMC-PPOLICY"


class AuditActions:
    PPOLICY_MOD_USER_ATTR = "PPOLICY_MOD_USER_ATTR"
    PPOLICY_DEL_USER_ATTR = "PPOLICY_DEL_USER_ATTR"
    PPOLICY_ADD_USER_PPOLICY = "PPOLICY_ADD_USER_PPOLICY"
    PPOLICY_MOD_USER_PPOLICY = "PPOLICY_MOD_USER_PPOLICY"
    PPOLICY_DEL_USER_PPOLICY = "PPOLICY_DEL_USER_PPOLICY"
    PPOLICY_MOD_ATTR = "PPOLICY_MOD_ATTR"
    PPOLICY_DEL_ATTR = "PPOLICY_DEL_ATTR"


AA = AuditActions


class AuditTypes(AT):
    PPOLICY = "PPOLICY"


AT = AuditTypes
