# -*- coding: utf-8; -*-
#
# (c) 2011 Mandriva, http://www.mandriva.com
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
 Provide tools to compute components version
"""

import re

r_revision = re.compile(r'\$Rev:\s*(\d+)\s*\$')

def scmRevision(prop):
    """ Extract revision number from $Rev$ svn property if it matches:
    $Rev: XXX$
    If prop is $Rev$, that means we are not on a svn repository.
    """
    r = r_revision.match(prop)
    return r and int(r.group(1)) or ''
