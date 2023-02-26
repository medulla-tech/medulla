# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2011 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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
