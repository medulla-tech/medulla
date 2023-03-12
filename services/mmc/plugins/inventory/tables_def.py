
# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
FIXME: find a docstring
"""

from mmc.support.mmctools import Singleton


class PossibleQueries(Singleton):
    def init(self, config):
        self.list = config.list
        self.double = config.double
        self.halfstatic = config.halfstatic
        self.extended = config.extended

    def possibleQueries(self, value=None):  # TODO : need to put this in the conf file
        if value == None:
            return {
                "list": self.list,
                "double": self.double,
                "halfstatic": self.halfstatic,
                "extended": self.extended,
            }
        else:
            if hasattr(self, value):
                return getattr(self, value)
            return []
