# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com
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
This module just give access to small functions needed by both 0.7 and 0.8 backend
"""

from pulse2.utils import grepv
import exceptions
import logging

def encode_utf8(self, s): return s
def encode_latin1(self, s):
    try:
        return s.decode('utf8')
    except exceptions.UnicodeEncodeError, e:
        return s
    except AttributeError:
        # under python 2.3, unicode object dont have any decode method
        # but in the case it's already a unicode, we dont really need to decode
        # so just return the string
        return s

def decode_utf8(self, s): return s
def decode_latin1(self, s):
    try:
        return s.decode('latin-1')
    except exceptions.UnicodeEncodeError, e:
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

def toUUID(id):
    return "UUID%s" % (str(id))

def setUUID(obj):
    if hasattr(obj, 'id'):
        setattr(obj, 'uuid', toUUID(obj.id))
    elif hasattr(obj, 'ID'):
        setattr(obj, 'uuid', toUUID(obj.ID))
    else:
        logging.getLogger().error("Can't get id for %s => no UUID"%(str(obj)))
    return obj

