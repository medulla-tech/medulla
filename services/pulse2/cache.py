# -*- coding: utf-8; -*-
#
# (c) 2011 Mandriva, http://www.mandriva.com/
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
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
This implements an generic object cache, with time-based expiration
"""
import time

from pulse2.utils import Singleton

DEFAULT_TIMEOUT = 10
TIMEOUT_FOREVER = -1

class CacheManager(Singleton):
    def __init__(self):
        self._caches = {}
        
    def getCache(self, name, timeout):
        try:
            ret = self._caches[name]
        except KeyError:
            ret = Cache(self, name, timeout)
            self._caches[name] = ret
        return ret

    def reset(self):
        self._caches = {}

def getCache(name, timeout=DEFAULT_TIMEOUT):
    cm = CacheManager()
    return cm.getCache(name, timeout)

class Cache(object):
    
    def __init__(self, manager, name, timeout=DEFAULT_TIMEOUT):
        """ timeout: time after which object expires, by default (seconds)
        """
        self.name = name
        self.timeout = timeout
        self._manager = manager
        self._data = {}

    def setTimeout(self, timeout):
        self.timeout = timeout

    def get(self, obj):
        try:
            (val, expires) = self._data[obj]
            if time.time() > expires:
                # If object has expired, remove it from cache
                del self._data[obj]
                raise CacheExpired()
        except KeyError:
            raise CacheFault()
        return val

    def set(self, obj, val, timeout=None):
        if timeout==TIMEOUT_FOREVER:
            # Never expires
            expires = 0
        elif timeout is None:
            expires = time.time() + self.timeout
        else:
            expires = time.time() + timeout
        self._data[obj] = (val, expires)

"""
Cache exceptions
"""
class CacheFault(Exception):
    """ Object is not present in cache
    """
    pass

class CacheExpired(Exception):
    """ Object is not valid anymore
    """
    pass
