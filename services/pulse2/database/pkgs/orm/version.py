# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

""" Class to map pkgs.version to SA
"""


class Version(object):
    """Mapping between pkgs.version and SA
    Well, nothing to map for
    """

    def getDbVersion(self):
        return self.version
