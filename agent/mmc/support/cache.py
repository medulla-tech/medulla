# -*- coding: utf-8; -*-
#
# (c) 2011 Mandriva, http://www.mandriva.com
#
# $Id: cache.py 820 2011-11-07 17:58:13Z jparpaillon $
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

"""
Provides a generic cache system

Cache class mainly taken from Django:
https://code.djangoproject.com/browser/django/trunk/django/core/cache/backends/locmem.py
"""
import time
import threading
import logging

log = logging.getLogger()

# Global in-memory store of cache data. Keyed by name, to provide
# multiple named local memory caches.
_caches = {}
_expire_info = {}
_locks = {}

TIMEOUT_DEFAULT = 300
TIMEOUT_INFINITE = -1

MAX_ENTRIES_DEFAULT = 300
CULL_FREQUENCY_DEFAULT = 3

class BaseCache(object):
    """ BaseCache is a Singleton
    """
    _instances = {}
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = object.__new__(cls)
            instance.init()
            cls._instances[cls] = instance
        return cls._instances[cls]

    def init(self, timeout=TIMEOUT_DEFAULT, max_entries=MAX_ENTRIES_DEFAULT,
             cull_frequency=CULL_FREQUENCY_DEFAULT):
        self.default_timeout = timeout
        self._max_entries = max_entries
        self._cull_frequency = cull_frequency

    def add(self, key, value, timeout=None):
        """
        Set a value in the cache if the key does not already exist. If
        timeout is given, that timeout will be used for the key; otherwise
        the default cache timeout will be used.

        Returns True if the value was stored, False otherwise.
        """
        raise NotImplementedError

    def get(self, key, default=None):
        """
        Fetch a given key from the cache. If the key does not exist, return
        default, which itself defaults to None.
        """
        raise NotImplementedError

    def set(self, key, value, timeout=None):
        """
        Set a value in the cache. If timeout is given, that timeout will be
        used for the key; otherwise the default cache timeout will be used.
        """
        raise NotImplementedError

    def delete(self, key):
        """
        Delete a key from the cache, failing silently.
        """
        raise NotImplementedError

    def get_many(self, keys):
        """
        Fetch a bunch of keys from the cache. For certain backends (memcached,
        pgsql) this can be *much* faster when fetching multiple values.

        Returns a dict mapping each key in keys to its value. If the given
        key is missing, it will be missing from the response dict.
        """
        d = {}
        for k in keys:
            val = self.get(k)
            if val is not None:
                d[k] = val
        return d

    def has_key(self, key):
        """
        Returns True if the key is in the cache and has not expired.
        """
        return self.get(key) is not None

    def incr(self, key, delta=1):
        """
        Add delta to value in the cache. If the key does not exist, raise a
        ValueError exception.
        """
        value = self.get(key)
        if value is None:
            raise ValueError("Key '%s' not found" % key)
        new_value = value + delta
        self.set(key, new_value)
        return new_value

    def decr(self, key, delta=1):
        """
        Subtract delta from value in the cache. If the key does not exist, raise
        a ValueError exception.
        """
        return self.incr(key, -delta)

    def __contains__(self, key):
        """
        Returns True if the key is in the cache and has not expired.
        """
        # This is a separate method, rather than just a copy of has_key(),
        # so that it always has the same functionality as has_key(), even
        # if a subclass overrides it.
        return self.has_key(key)

    def set_many(self, data, timeout=None):
        """
        Set a bunch of values in the cache at once from a dict of key/value
        pairs.  For certain backends (memcached), this is much more efficient
        than calling set() multiple times.

        If timeout is given, that timeout will be used for the key; otherwise
        the default cache timeout will be used.
        """
        for key, value in data.items():
            self.set(key, value, timeout=timeout)

    def delete_many(self, keys):
        """
        Set a bunch of values in the cache at once.  For certain backends
        (memcached), this is much more efficient than calling delete() multiple
        times.
        """
        for key in keys:
            self.delete(key)

    def clear(self):
        """Remove *all* values from the cache at once."""
        raise NotImplementedError

class LocMemCache(BaseCache):
    DEFAULT_NAME = "default"

    def __init__(self, name=None, *args, **kwargs):
        global _caches, _expire_info, _locks
        super(LocMemCache, self).__init__(*args, **kwargs)

        if name is None:
            name = self.DEFAULT_NAME
        self._cache = _caches.setdefault(name, {})
        self._expire_info = _expire_info.setdefault(name, {})
        self._lock = _locks.setdefault(name, RWLock())

    def add(self, key, value, timeout=None):
        self._lock.writer_enters()
        try:
            exp = self._expire_info.get(key)
            if exp is None or exp <= time.time():
                self._set(key, value, timeout)
                return True
            return False
        finally:
            self._lock.writer_leaves()

    def get(self, key, default=None):
        log.debug("Get cache value: %s" % (key, ))
        self._lock.reader_enters()
        try:
            exp = self._expire_info.get(key)
            if exp is None:
                return default
            elif exp > time.time():
                return self._cache[key]
        finally:
            self._lock.reader_leaves()
        self._lock.writer_enters()
        try:
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return default
        finally:
            self._lock.writer_leaves()

    def _set(self, key, value, timeout=None):
        if len(self._cache) >= self._max_entries:
            self._cull()
        if timeout is None:
            timeout = self.default_timeout
        self._cache[key] = value
        self._expire_info[key] = time.time() + timeout

    def set(self, key, value, timeout=None):
        log.debug("Set cache value: %s=%r" % (key, value))
        self._lock.writer_enters()
        try:
            self._set(key, value, timeout)
        finally:
            self._lock.writer_leaves()

    def has_key(self, key):
        self._lock.reader_enters()
        try:
            exp = self._expire_info.get(key)
            if exp is None:
                return False
            elif exp > time.time():
                return True
        finally:
            self._lock.reader_leaves()

        self._lock.writer_enters()
        try:
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return False
        finally:
            self._lock.writer_leaves()

    def _cull(self):
        if self._cull_frequency == 0:
            self.clear()
        else:
            doomed = [k for (i, k) in enumerate(self._cache) if i % self._cull_frequency == 0]
            for k in doomed:
                self._delete(k)

    def _delete(self, key):
        try:
            del self._cache[key]
        except KeyError:
            pass
        try:
            del self._expire_info[key]
        except KeyError:
            pass

    def delete(self, key):
        self._lock.writer_enters()
        try:
            self._delete(key)
        finally:
            self._lock.writer_leaves()

    def clear(self):
        self._cache.clear()
        self._expire_info.clear()

###
### Various generic or specialized cached objects
###
def genericHashFunc(*args, **kwargs):
    def freeze(o):
        if isinstance(o, list) or isinstance(o, tuple):
            return tuple(map(lambda x: freeze(x), o))
        elif isinstance(o, dict):
            return freeze(o.items())
        else:
            return o

    try:
        arghash = hash(freeze(args))
    except TypeError:
        return None

    try:
        kwhash = hash(freeze(kwargs))
    except TypeError:
        return None
    return (arghash, kwhash)

class CacheableObject(object):
    """ Object whose methods can be cached
    """
    CACHE_NAME = "defaultcache"

    def __init__(self, *args, **kwargs):
        super(CacheableObject, self).__init__(*args, **kwargs)
        self.cache = LocMemCache()

    def _cached(self, method, key=None, *args, **kwargs):
        if key is None:
            raise ValueError("Invalid cache key: None")
        
        if self.cache.has_key(key):
            ret = self.cache.get(key)
            log.debug("%s(%s, %s): key=%s, value=%s" % (method.__name__,
                                                        args, kwargs,
                                                        key, ret))
        else:
            ret = method(self, *args, **kwargs)
            self.cache.set(key, ret)
            log.debug("%s(%s, %s): key=%s, value=<EMPTY CACHE>" % (method.__name__,
                                                                   args, kwargs,
                                                                   key))
        return ret


from twisted.internet import defer
class _DeferredCache(object):
    """ Wraps a call that returns a deferred in a cache. Any subsequent
    calls with the same argument will wait for the first call to finish and
    return the same result (or errback)
    Got on:
    http://twistedmatrix.com/pipermail/twisted-python/2005-January/009299.html
    """
    def __init__(self, op, hashFunc=None):
        self.op = op
        self.cache = LocMemCache(op.func_name)
        if hashFunc is None:
            self.hashFunc = genericHashFunc
        else:
            self.hashFunc = hashFunc

    def cb_triggerUserCallback(self, res, deferred):
        deferred.callback(res)
        return res

    def cb_triggerUserErrback(self, failure, deferred):
        deferred.errback(failure)
        return failure

    def call(self, *args, **kwargs):
        # Currently not in progress - start it
        key = self.hashFunc(*args, **kwargs)
        if key is None:
            log.debug("DeferredCache(%s) not hashable: not caching. " % self.op.func_name)
            return self.op(*args, **kwargs)

        if self.cache.has_key(key):
            log.debug("DeferredCache(%s): using cache" % self.op.func_name)
            opDeferred = self.cache.get(key)
        else:
            log.debug("DeferredCache(%s): caching" % self.op.func_name)
            opDeferred = self.op(*args, **kwargs)
            self.cache.set(key, opDeferred)

        userDeferred = defer.Deferred()
        opDeferred.addCallback(lambda x: self.cb_triggerUserCallback(x, userDeferred))
        opDeferred.addErrback(lambda x: self.cb_triggerUserErrback(x, userDeferred))
        return userDeferred

def DeferredCache(op, hashFunc=None):
    c = _DeferredCache(op, hashFunc=hashFunc)
    def func(*args, **kwargs):
        return c.call(*args, **kwargs)
    return func

###
### reader-writer lock (preference to writers)
### From Django
###

class RWLock:
    """
    Classic implementation of reader-writer lock with preference to writers.

    Readers can access a resource simultaneously.
    Writers get an exclusive access.

    API is self-descriptive:
        reader_enters()
        reader_leaves()
        writer_enters()
        writer_leaves()
    """
    def __init__(self):
        self.mutex     = threading.RLock()
        self.can_read  = threading.Semaphore(0)
        self.can_write = threading.Semaphore(0)
        self.active_readers  = 0
        self.active_writers  = 0
        self.waiting_readers = 0
        self.waiting_writers = 0

    def reader_enters(self):
        self.mutex.acquire()
        try:
            if self.active_writers == 0 and self.waiting_writers == 0:
                self.active_readers += 1
                self.can_read.release()
            else:
                self.waiting_readers += 1
        finally:
            self.mutex.release()
        self.can_read.acquire()

    def reader_leaves(self):
        self.mutex.acquire()
        try:
            self.active_readers -= 1
            if self.active_readers == 0 and self.waiting_writers != 0:
                self.active_writers  += 1
                self.waiting_writers -= 1
                self.can_write.release()
        finally:
            self.mutex.release()

    def writer_enters(self):
        self.mutex.acquire()
        try:
            if self.active_writers == 0 and self.waiting_writers == 0 and self.active_readers == 0:
                self.active_writers += 1
                self.can_write.release()
            else:
                self.waiting_writers += 1
        finally:
            self.mutex.release()
        self.can_write.acquire()

    def writer_leaves(self):
        self.mutex.acquire()
        try:
            self.active_writers -= 1
            if self.waiting_writers != 0:
                self.active_writers  += 1
                self.waiting_writers -= 1
                self.can_write.release()
            elif self.waiting_readers != 0:
                t = self.waiting_readers
                self.waiting_readers = 0
                self.active_readers += t
                while t > 0:
                    self.can_read.release()
                    t -= 1
        finally:
            self.mutex.release()
