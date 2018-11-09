# -*- coding: utf-8; -*-
#
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
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

from sqlalchemy.orm import Query
from sqlalchemy.exc import DBAPIError

import logging

def unique(s):
    """Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        pass  # move on to the next method
    else:
        return u.keys()

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        pass  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u

def create_method(m):
    # 'm' if the name of the method to override
    def method(self, already_in_loop = False):
        # WARNING: recursive function, so 'already_in_loop' necessary for
        # us to know if we are recursing (True) or not (False)
        NB_DB_CONN_TRY = 2

        # FIXME: NOT YET IMPLEMENTED, but do not implement this using a
        # simple time.sleep(), it would lock the main loop !!!
        #TIME_BTW_CONN_TRY = 0.1 # in seconds, floats are authorized, # pyflakes.ignore

        try: # do a libmysql client call : attempt to perform the old call (_old_<method>)
            old_m = getattr(self, '_old_%s' % m)
            ret = old_m() # success, will send the result back
            return ret # send the result back
        except DBAPIError, e: # failure, catch libmysql client error
            if already_in_loop : # just raise the exception, they will take care of it
                raise e

            # see http://dev.mysql.com/doc/refman/5.1/en/error-messages-client.html
            # we try to handle only situation where a reconnection worth a try
            if e.orig.args[0] == 2013: # Lost connection to MySQL server during query error, but we do not raise the exception (will attempt again)
                logging.getLogger().warn("Lost connection to MySQL server during query")
            elif e.orig.args[0] == 2006: # MySQL server has gone away, but we do not raise the exception (will attempt again)
                logging.getLogger().warn("MySQL server connection has gone away")
            elif e.orig.args[0] == 2002: # Can't contact SQL server, give up
                logging.getLogger().error("MySQL server is unreachable by socket while doing query")
                raise e
            elif e.orig.args[0] == 2003: # Can't contact SQL server, give up
                logging.getLogger().error("MySQL server is unreachable by network while doing query")
                raise e
            else: # Other SQL error, give-up
                logging.getLogger().error("Unknown MySQL error while doing query")
                raise e

            # handle cases where reco can be attempted again
            # this is where things became tricky:
            # we call ourself (new_m) with already_in_loop = True
            # we also silently drop the potentially raised exception
            for i in range(0, NB_DB_CONN_TRY):
                try:
                    new_m = getattr(self, m)
                    ret = new_m(True)
                    return ret
                except Exception, e:
                    pass

            # the loop was unsuccessful, finally raise the original exception
            raise e
    return method

def handle_deconnect():
    # initialize "disconnection handling" code
    # base principle : sensitive methods ('first', 'count', 'all', '__iter__') are
    #  - renamed to _old_<method>
    #  - replaced by create_method
    # create_method then call _old_<method> on demand (see upper)
    for m in ['first', 'count', 'all', '__iter__']:
        try: # check if _old_<method> exists
            getattr(Query, '_old_%s' % m)
        except AttributeError: # and if not, create it
            setattr(Query, '_old_%s' % m, getattr(Query, m))
            setattr(Query, m, create_method(m))

def toH(w):
    ret = {}
    for i in filter(lambda f: not f.startswith('__'), dir(w)):
        ret[i] = getattr(w, i)
    return ret

def toUUID(id):
    return "UUID%s" % (str(id))

def fromUUID(uuid):
    return int(uuid.replace('UUID', ''))

class DbObject(object):
    def toH(self):
        ret = {}
        for i in filter(lambda f: not f.startswith('_'), dir(self)):
            t = type(getattr(self, i))
            if t == str or t == dict or t == unicode or t == tuple or t == int or t == long:
                ret[i] = getattr(self, i)
        ret['uuid'] = toUUID(getattr(self, 'id'))
        return ret
