# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import re

from mmc.support.mmctools import shLaunch

def get_keychain():
    proc = shLaunch('uname -n')
    p1 = re.compile('\n')
    out = p1.split(proc.out)

    if os.path.exists('/root/.keychain/'+out[0]+'-sh'):
        f=open('/root/.keychain/'+out[0]+'-sh', 'r')
        file = f.read()
        lines = p1.split(file)

        proc = shLaunch('env '+lines[0])
        return proc.out

    return ''

