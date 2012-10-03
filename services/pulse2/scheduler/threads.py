# -*- coding: utf-8; -*-
#
# (c) 2012 Mandriva, http://www.mandriva.com/
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

# big modules
import time
import sys
import threading
import logging

# twisted stuff
import twisted.internet.reactor
import twisted.internet.defer
import twisted.python

# our stuff
from pulse2.scheduler.config import SchedulerConfig

def runInThread(function, *args, **kwargs):
    def _cbSuccess(result, deferred,):
       	twisted.internet.reactor.callFromThread(deferred.callback, result)

    def _cbFailure(failure, deferred):
        twisted.internet.reactor.callFromThread(deferred.errback, failure)

    def _putResult(deferred, function, args, kwargs):
        start=time.time()
        logging.getLogger().debug('scheduler "%s": THREAD: Thread #%s : start %s' % (SchedulerConfig().name, threading.currentThread().getName().split("-")[2], function.__name__))
        try:
            result = function(*args, **kwargs)
        except:
            logging.getLogger().error('scheduler "%s": THREAD: Thread #%s : error %s' % (SchedulerConfig().name, threading.currentThread().getName().split("-")[2], sys.exc_info()[0]))
            twisted.internet.reactor.callFromThread(deferred.errback, twisted.python.failure.Failure())
        else:
            if isinstance(result, twisted.internet.defer.Deferred):
                result.addCallback(_cbSuccess, deferred)
                result.addErrback(_cbFailure, deferred)
            else:
                twisted.internet.reactor.callFromThread(deferred.callback, result)
        logging.getLogger().debug('scheduler "%s": THREAD: Thread #%s : passed %s' % (SchedulerConfig().name, threading.currentThread().getName().split("-")[2], time.time()-start))

    d = twisted.internet.defer.Deferred()
    twisted.internet.reactor.callInThread(_putResult, d, function, args, kwargs)
    return d


