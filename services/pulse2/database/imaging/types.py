# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
Types to use in the imaging pluging
"""


class Pulse2ImagingSynchroStates:
    TODO = 1
    DONE = 2
    RUNNING = 3
    INIT_ERROR = 4 # when the init of a target failed on the pserver side
P2ISS = Pulse2ImagingSynchroStates


class Pulse2ImagingTypes:
    COMPUTER = 1
    PROFILE = 2
    COMPUTER_IN_PROFILE = 3
    ALL_COMPUTERS = 4
    DELETED_COMPUTER = 5
P2IT = Pulse2ImagingTypes


class Pulse2ImagingMenu:
    ALL = 10
    BOOTSERVICE = 11
    IMAGE = 12
P2IM = Pulse2ImagingMenu


class Pulse2ImagingImageKind:
    IS_BOTH = 20
    IS_MASTER_ONLY = 21
    IS_IMAGE_ONLY = 22
P2IIK = Pulse2ImagingImageKind


class Pulse2ImagingErrors:
    ERR_DEFAULT = 1000
    ERR_MISSING_NOMENCLATURE = 1001
    ERR_IMAGING_SERVER_DONT_EXISTS = 1003
    ERR_ENTITY_ALREADY_EXISTS = 1004
    ERR_UNEXISTING_MENUITEM = 1005
    ERR_TARGET_HAS_NO_MENU = 1006
    ERR_ENTITY_HAS_NO_DEFAULT_MENU = 1007
    ERR_IMAGE_ALREADY_EXISTS = 1008
    ERR_COMPUTER_ALREADY_EXISTS = 1009

P2ERR = Pulse2ImagingErrors


class Pulse2ImagingLogStates:
    UNKNOWN = 1
    BOOT = 2
    MENU = 3
    RESTORATION = 4
    BACKUP = 5
    POSTINSTALL = 6
    ERROR = 7
    DELETE = 8
P2ILS = Pulse2ImagingLogStates


class Pulse2ImagingLogLevel:
    LOG_EMERG = 0
    LOG_ALERT = 1
    LOG_CRIT = 2
    LOG_ERR = 3
    LOG_WARNING = 4
    LOG_NOTICE = 5
    LOG_INFO = 6
    LOG_DEBUG = 7
P2ILL = Pulse2ImagingLogLevel

