# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import re
import os


def addslashes(str):
    # need to check if it doesn't already exists
    p1 = re.compile("'")
    return p1.sub("\\'", str)


def escapeshellarg(str):
    p1 = re.compile('"')
    str = p1.sub('"', str)
    return '"' + str + '"'


def clean_path(str):
    return os.path.realpath(str)
