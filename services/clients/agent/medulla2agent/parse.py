# -*- test-case-name: medulla.msc.client.tests.parse -*-
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later


class Parser(object):
    """A simple wrapper for several serializers"""

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
                import pickle

                self._backend = cPickle
            except ImportError:
                import pickle

                self._backend = pickle
        else:
            raise TypeError(f"Unknown parser type: {backend}")

    def encode(self, value):
        return self._backend.dumps(value)

    def decode(self, value):
        return self._backend.loads(value)
