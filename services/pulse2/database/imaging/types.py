# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id: config.py 4804 2009-11-20 10:02:33Z oroussy $
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
PULSE2_IMAGING_SYNCHROSTATE_TODO = 1
PULSE2_IMAGING_SYNCHROSTATE_DONE = 2
PULSE2_IMAGING_SYNCHROSTATE_RUNNING = 3
PULSE2_IMAGING_SYNCHROSTATE_INIT_ERROR = 4 # when the init of a target failed on the pserver side

PULSE2_IMAGING_TYPE_COMPUTER=1
PULSE2_IMAGING_TYPE_PROFILE=2

PULSE2_IMAGING_MENU_ALL=10
PULSE2_IMAGING_MENU_BOOTSERVICE=11
PULSE2_IMAGING_MENU_IMAGE=12

PULSE2_IMAGING_IMAGE_IS_BOTH=20
PULSE2_IMAGING_IMAGE_IS_MASTER_ONLY=21
PULSE2_IMAGING_IMAGE_IS_IMAGE_ONLY=22

