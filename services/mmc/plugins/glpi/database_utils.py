# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText:2007-2014 Mandriva, http://www.mandriva.com
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This module just give access to small functions needed by both 0.7 and 0.8 backend
"""

from pulse2.utils import grepv
import exceptions
import logging

def encode_utf8(self, s):
    return s

def encode_latin1(self, s):
    try:
        return s.decode('utf8')
    except exceptions.UnicodeEncodeError:
        return s
    except AttributeError:
        # under python 2.3, unicode object dont have any decode method
        # but in the case it's already a unicode, we dont really need to decode
        # so just return the string
        return s

def decode_utf8(self, s):
    return s

def decode_latin1(self, s):
    try:
        return s.decode('latin-1')
    except exceptions.UnicodeEncodeError:
        return s

class DbTOA(object):
    def to_a(self):
        a = grepv('^_', dir(self))
        ret = []
        for i in a:
            j = getattr(self, i)
            if type(j) in (str, int, unicode):
                ret.append([i, j])
        return ret

def fromUUID(uuid):
    return int(uuid.replace('UUID', ''))

def toUUID(uuid):
    return "UUID%s" % (str(uuid))

def setUUID(obj):
    if hasattr(obj, 'id'):
        setattr(obj, 'uuid', toUUID(obj.id))
    elif hasattr(obj, 'ID'):
        setattr(obj, 'uuid', toUUID(obj.ID))
    else:
        logging.getLogger().error("Can't get id for %s => no UUID"%(str(obj)))
    return obj
