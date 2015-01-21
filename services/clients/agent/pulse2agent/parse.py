# -*- test-case-name: pulse2.msc.client.tests.parse -*-
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


class Parser(object):
    """ A simple wrapper for several serializers """

    def __init__(self, backend="json"):
        self._set_backend(backend)


    def _set_backend(self, backend):
        if backend == "json":
            import json
            self._backend = json

        elif backend == "marshal":
            import marshal
            self._backend = marshal

        elif backend == "pickle":
            try:
                import cPickle
                self._backend = cPickle
            except ImportError:
                import pickle
                self._backend = pickle
        else:
            raise TypeError, "Unknown parser type: %s" % backend

    def encode(self, value):
        return self._backend.dumps(value)

    def decode(self, value):
        return self._backend.loads(value)


