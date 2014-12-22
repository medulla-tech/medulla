# -*- test-case-name: pulse2.cm.tests.server -*-
# -*- coding: utf-8; -*-
#
# (c) 2014 Mandriva, http://www.mandriva.com/
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

"""
An universal buffer to queue incoming requests.

Several tasks on servers can be heavy and processing them
can take a lot of time and block other tasks allocating
a part of resources.

The goal of this solution is to queue incoming request
and store only its reference to avoid chaining a lot
of operations until the returning a result.

- All the requests are queued into a LIFO register
  and released from there when a service processing
  the requests have availables resources.
- When a result is returned, its referenced session
  fires a deferred with result as reason.

We can define a timeout to limit the processing time of request.
"""

import time
from twisted.internet import reactor

from twisted.internet.defer import Deferred, DeferredQueue
from twisted.internet.defer import CancelledError, succeed
from twisted.internet.task import deferLater



class SessionNotFound(Exception):
    """ Similar to IndexError - session not found in container"""

    def __init__(self, uid):
        Exception.__init__(self)
        self.uid = uid

    def __repr__(self):
        return "Session <%s> not found" % repr(self.uid)



class Sessions(object):
    """
    A session tracker generating the deferreds as main elements.

    Stored references of created deferred can be used outside
    and gathered here by its idetifiers.

    A simple maker of session creates a deferred and its unique
    identifier. This deferred is stored into the internal dictionnary.
    """

    _id = 0
    content = {}

    expirators = {}

    def __init__(self, result_if_expire=False, timeout=3600, clock=reactor):
        """
        @param result_if_expire: reason of expired deferred
        @type result_if_expire: any

        @param timeout: timeout of element since adding
        @type timeout: int

        @param clock: reactor instance
        @type clock: clock
        """

        self._id = 0
        self.clock = clock
        self.content = {}
        self._timeout = timeout
        self._result_if_expire = result_if_expire


    def _inc(self):
        """
        Increments internal counter.

        @return: generated value
        @rtype: int
        """
        self._id += 1
        return self._id


    def make(self):
        """
        Creates and add a deferred with unique identifier in container.

        @return: identifier of session and a new deferred
        @rtype: tuple
        """

        uid = self._inc()

        deferred = Deferred()
        timestamp = time.time()

        self.content[uid] = (timestamp, deferred)

        # timeout declaration
        expirator = deferLater(self.clock,
                               self._timeout,
                               self._expire,
                               uid)

        # when expirator is cancelled, a errorback is fired
        expirator.addErrback(self._eb_expirator)

        self.expirators[uid] = expirator

        return uid, deferred


    def __contains__(self, uid):
        """
        Membership test operator.

        @param uid: uid of request
        @type uid: int

        @return: True if task present
        @rtype: bool
        """
        return uid in self.content


    def remove(self, uid):
        """
        Removes a session.

        @param uid: identifier of session
        @type uid: int

        @raises: SessionNotFound if session not exists
        """
        if uid in self:
            del self.content[uid]

            exp = self.expirators[uid]
            exp.cancel()
            del self.expirators[uid]
        else:
            raise SessionNotFound, uid


    def get(self, uid):
        """
        Returns a session.

        @param uid: identifier of session
        @type uid: int

        @return: found session
        @rtype: deferred

        @raises: SessionNotFound if session not exists
        """

        if uid in self:
            timestamp, deferred = self.content[uid]
            return deferred
        else:
            raise SessionNotFound, uid

    def pop(self, uid):
        """
        Pops a session.

        @param uid: identifier of session
        @type uid: int

        @return: found session
        @rtype: deferred

        @raises: SessionNotFound if session not exists
        """
        deferred = self.get(uid)
        self.remove(uid)
        return deferred



    def _expire(self, uid):
        """
        Removes expired sessions.

        """
        deferred = self.get(uid)
        deferred.callback(self._result_if_expire)
        self.remove(uid)

    def _eb_expirator(self, failure):
        """
        A fallback of deferred of expirator.

        This errorback is called always when expirator is cancelled
        before removing from internal container of expirators.

        """
        e = failure.trap(CancelledError)
        if e == CancelledError:
            pass
            # expirator successfully cancelled
        else:
            print "expirator failed: %s" % str(failure)
            return failure


class Collector(object):
    """
    Provides a smart buffer of request.

    Because some requests can be long and heavy, this provider
    allows to put the requests into a queue where other side may
    treat previous requests until last added.

    During making of each request, an identifier and a new deferred
    is created. This deferred is assigned to incomming session
    of request which is waiting with its unfired deffered.

    When queued request is processed and a result is returned,
    waiting related deferred is fired with this result.
    """

    queue = None
    sessions = None

    def __init__(self, sessions=Sessions()):
        self.queue = []

        self.sessions = sessions


    def queue_and_process(self, ip, request):
        """
        Inserts request into the queue.

        Each queued request returns a deferred which will be fired
        when a queued element is processed.

        @param request
        """
        uid, deferred = self.sessions.make()
        self.queue.append((uid, ip, request))

        return deferred


    def get(self):
        """
        Returns uid and request data as PacketRef object.

        This method should be called by a service processing requests
        to get a request specification. This request is released from
        internal queue, but its deferred still stored in session tracker.

        @return: uuid and request
        @rtype: deferred
        """
        try:
            uid, ip, request = self.queue.pop(0)
            if uid in self.sessions:
                return (uid, ip, request)
            else:
                return None
        except IndexError:
            return None



    def release(self, uid, result):
        """
        Releases queued request and fires related deferred.

        @param uid: session identifier
        @type uid: int

        @param result: reason of fired deferred
        @type result: any

        @return: fired deferred - can be useful to chain another action
        @rtype: Deferred
        """

        deferred = self.sessions.pop(uid)
        deferred.callback(result)

        return deferred

