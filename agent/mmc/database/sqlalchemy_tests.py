# -*- coding: utf-8; -*-
#
# (c) 2008-2009 Mandriva, http://www.mandriva.com/
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
from distutils.version import StrictVersion
from sqlalchemy import __version__

MIN_VERSION = '0.6.3' # Debian Squeeze version
MAX_VERSION = '0.9.8' # Debian Jessie version
CUR_VERSION = __version__

def checkSqlalchemy():
    #if MIN_VERSION <= CUR_VERSION <= MAX_VERSION:
    if StrictVersion(MIN_VERSION) <= StrictVersion(CUR_VERSION) <=  StrictVersion(MAX_VERSION) :
        return True
    else:
        return False
