# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
This module define the user package_api API
It provide methods to tell which package_api a user can use to modify packages.
"""

from pulse2.apis.clients import Pulse2Api


class UserPackageApiApi(Pulse2Api):
    def __init__(self, *attr):
        self.name = "UserPackageApiApi"
        Pulse2Api.__init__(self, *attr)

    def getUserPackageApi(self, user):
        if self.initialized_failed:
            return {}
        d = self.callRemote("getUserPackageApi", {"name": user, "uuid": user})
        d.addErrback(
            self.onError,
            "UserPackageApiApi:getUserPackageApi",
            {"name": user, "uuid": user},
            [
                {
                    "ERR": "PULSE2ERROR_GETUSERPACKAGEAPI",
                    "mirror": self.server_addr.replace(self.credentials, ""),
                }
            ],
        )
        return d
