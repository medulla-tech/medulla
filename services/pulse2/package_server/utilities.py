#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
    Pulse2 Modules
"""

import hashlib
import sys


def sumfile(fobj):
    """Returns an md5 hash for an object with read() method."""
    m = hashlib.new("md5")
    while True:
        d = fobj.read(8096)
        if not d:
            break
        m.update(d)
    return m.hexdigest()


def md5file(fname):
    """Returns an md5 hash for file fname, or stdin if fname is "-"."""
    if fname == "-":
        ret = sumfile(sys.stdin)
    else:
        try:
            f = open(fname, "rb")
        except BaseException:
            return "Failed to open file"
        ret = sumfile(f)
        f.close()
    return ret


def md5sum(str):
    return hashlib.md5(str).hexdigest()
