# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

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
        return list(u.keys())

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = sorted(s)
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
    def method(self, already_in_loop=False):
        # WARNING: recursive function, so 'already_in_loop' necessary for
        # us to know if we are recursing (True) or not (False)
        NB_DB_CONN_TRY = 2

        # FIXME: NOT YET IMPLEMENTED, but do not implement this using a
        # simple time.sleep(), it would lock the main loop !!!
        # TIME_BTW_CONN_TRY = 0.1 # in seconds, floats are authorized, # pyflakes.ignore

        try:  # do a libmysql client call : attempt to perform the old call (_old_<method>)
            old_m = getattr(self, f"_old_{m}")
            ret = old_m()  # success, will send the result back
            return ret  # send the result back
        except DBAPIError as e:  # failure, catch libmysql client error
            if already_in_loop:  # just raise the exception, they will take care of it
                raise e

            # see http://dev.mysql.com/doc/refman/5.1/en/error-messages-client.html
            # we try to handle only situation where a reconnection worth a try
            if (
                e.orig.args[0] == 2013
            ):  # Lost connection to MySQL server during query error, but we do not raise the exception (will attempt again)
                logging.getLogger().warn("Lost connection to MySQL server during query")
            elif (
                e.orig.args[0] == 2006
            ):  # MySQL server has gone away, but we do not raise the exception (will attempt again)
                logging.getLogger().warn("MySQL server connection has gone away")
            elif e.orig.args[0] == 2002:  # Can't contact SQL server, give up
                logging.getLogger().error(
                    "MySQL server is unreachable by socket while doing query"
                )
                raise e
            elif e.orig.args[0] == 2003:  # Can't contact SQL server, give up
                logging.getLogger().error(
                    "MySQL server is unreachable by network while doing query"
                )
                raise e
            else:  # Other SQL error, give-up
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
                except Exception as e:
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
    for m in ["first", "count", "all", "__iter__"]:
        try:  # check if _old_<method> exists
            getattr(Query, f"_old_{m}")
        except AttributeError:  # and if not, create it
            setattr(Query, f"_old_{m}", getattr(Query, m))
            setattr(Query, m, create_method(m))


def toH(w):
    return {
        i: getattr(w, i) for i in [f for f in dir(w) if not f.startswith("__")]
    }


def toUUID(id):
    return f"UUID{str(id)}"


def fromUUID(uuid):
    return int(uuid.replace("UUID", ""))


class DbObject(object):
    def toH(self):
        ret = {}
        for i in [f for f in dir(self) if not f.startswith("_")]:
            t = type(getattr(self, i))
            if t in [str, dict, tuple, int]:
                ret[i] = getattr(self, i)
        ret["uuid"] = toUUID(getattr(self, "id"))
        return ret
