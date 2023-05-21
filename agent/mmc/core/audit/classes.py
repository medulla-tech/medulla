# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
   Python classes describing the audit database model
"""


class Event(object):
    pass


class Source(object):
    pass


class Initiator(object):
    pass


class Current_Value(object):
    def __init__(self, object_log, value):
        self.object_log_id = object_log.id
        self.value = value


class Record(object):
    def getId(self):
        return self.id

    def __repr__(self):
        return [
            self.id,
            self.event_id,
            self.initiator_id,
            self.user_id,
            self.date,
            self.module_id,
            self.result,
        ]


class Object_Log(object):
    pass


class Object(object):
    pass


class Parameters(object):
    def __init__(self, param_name, value):
        self.param_name = param_name
        self.param_value = value


class Module(object):
    pass


class Previous_Value(object):
    def __init__(self, object_log, value):
        self.object_log_id = object_log.id
        self.value = value


class Type(object):
    pass


class Version(object):
    pass
