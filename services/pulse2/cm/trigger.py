# -*- test-case-name: pulse2.cm.tests.trigger -*-
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

from twisted.internet.defer import succeed, maybeDeferred


class Trigger(object):
    """
    Provides a reference to execute a callable.

    Instance of this object makes a bridge between gateway
    and endpoints which have to wake up the endpoints
    to looking for new requests.
    Method fire() must be called always when gateway recieves
    any data to queue.
    A callable with arguments passed trough the constructor
    may directly call the iterators from endpoints.
    """

    # This flag says that endpoints not finished yet
    locked = False


    def __init__(self, method, *args, **kwargs):
        """
        @param method: method calling the endpoints
        @type method: callable

        @param args: args of method
        @type args: list

        @param kwargs: kwargs of method
        @type kwargs: dict
        """
        self.logger = logging.getLogger()
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.locked = False

        self.scheduled_for_next = False



    def fire(self):
        """
        Method called when any data received.

        If all previous requests was terminated,
        method calling the endpoints is launched
        in a thread.
        If this method is called during the run
        of endpoints, new call is disallowed.

        @return: True if method of endpoints call finished
        @rtype: Deferred
        """

        if not self.locked:
            #d = deferToThread(self.method,
            d = maybeDeferred(self.method,
                             *self.args,
                             **self.kwargs
                             )
            self.locked = True
            @d.addErrback
            def failed(failure):
                self.logger.warn("Method <%s> calling failed: %s" % (self.method.__name__, str(failure)))
                return False
            @d.addCallback
            def finished(result):
                self.logger.debug("Method <%s> finished: %s" % (self.method.__name__, str(result)))
                self.locked = False
                return True


            return d

        else:
            print "not unlocked yet"
            return succeed(False)



if __name__ == "__main__":
    from twisted.internet import reactor

    def do_something(*args, **kwargs):
        import time
        time.sleep(2)

    t = Trigger(do_something)
    d = t.fire()
    @d.addCallback
    def aa(reason):
        print 'aa reason: %s' % str(reason)

    print "after 1st"

    d = t.fire()
    @d.addCallback
    def bb(reason):
        print 'bb reason: %s' % str(reason)


    print "after 2nd"

    reactor.run()



