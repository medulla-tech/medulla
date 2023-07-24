# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2011 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

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
        """timeout: time after which object expires, by default (seconds)"""
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
        if timeout == TIMEOUT_FOREVER:
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
    """Object is not present in cache"""

    pass


class CacheExpired(Exception):
    """Object is not valid anymore"""

    pass
