# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id$
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Constants for the audit framework and the ppolicy plugin.
"""

from mmc.plugins.base.audit import AT

PLUGIN_NAME = u'MMC-PPOLICY'

class AuditActions:
    PPOLICY_MOD_USER_ATTR = u'PPOLICY_MOD_USER_ATTR'
    PPOLICY_DEL_USER_ATTR = u'PPOLICY_DEL_USER_ATTR'
    PPOLICY_ADD_USER_PPOLICY = u'PPOLICY_ADD_USER_PPOLICY'
    PPOLICY_MOD_USER_PPOLICY = u'PPOLICY_MOD_USER_PPOLICY'
    PPOLICY_DEL_USER_PPOLICY = u'PPOLICY_DEL_USER_PPOLICY'
    PPOLICY_MOD_ATTR = u'PPOLICY_MOD_ATTR'
    PPOLICY_DEL_ATTR = u'PPOLICY_DEL_ATTR'
AA = AuditActions

class AuditTypes(AT):
    PPOLICY = u'PPOLICY'
AT = AuditTypes

