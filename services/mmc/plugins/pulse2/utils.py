#
# (c) 2010 Mandriva, http://www.mandriva.com/
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

"""
Pulse2 utils
"""

from mmc.support.mmctools import Singleton
from uuid import uuid4

class notificationManager(Singleton):
    
    notifications = []
    
    def add(self, module, title, content, priority=0):
        uuid = str(uuid4())
        self.notifications.append({
                'uuid': uuid,
                'module':module,
                'title':title,
                'content':content,
                'priority':priority,
                'seen': False
        })
        return uuid
        
    def getModuleNotification(self, module):
        # Sort them by priority
        return [n for n in self.notifications if n['module'] == module]
    
    def setAsSeen(self, notification_uuid):
        for i in xrange(len(self.notifications)):
            if self.notifications[i]['uuid'] == notification_uuid:
                self.notifications[i]['seen'] = True
                return self.notifications[i]
    
