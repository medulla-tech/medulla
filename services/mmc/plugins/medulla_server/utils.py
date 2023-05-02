# SPDX-FileCopyrightText: 2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Pulse2 utils
"""

from mmc.support.mmctools import Singleton
from uuid import uuid4


class notificationManager(Singleton):

    notifications = []

    def add(self, module, title, content, priority=0):
        uuid = str(uuid4())
        self.notifications.append(
            {
                "uuid": uuid,
                "module": module,
                "title": title,
                "content": content,
                "priority": priority,
                "seen": False,
            }
        )
        return uuid

    def getModuleNotification(self, module):
        # Sort them by priority
        return [n for n in self.notifications if n["module"] == module]

    def setAsSeen(self, notification_uuid):
        for i in range(len(self.notifications)):
            if self.notifications[i]["uuid"] == notification_uuid:
                self.notifications[i]["seen"] = True
                return self.notifications[i]
