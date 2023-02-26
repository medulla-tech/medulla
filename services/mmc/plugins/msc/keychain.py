# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import os
import re

from mmc.support.mmctools import shLaunch

#def get_keychain():
    #proc = shLaunch('uname -n')
    #p1 = re.compile('\n')
    #out = p1.split(proc.out)

    #if os.path.exists('/root/.keychain/'+out[0]+'-sh'):
        #f=open('/root/.keychain/'+out[0]+'-sh', 'r')
        #file = f.read()
        #lines = p1.split(file)

        #proc = shLaunch('env '+lines[0])
        #return proc.out

    #return ''
