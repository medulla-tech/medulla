# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
from ConfigParser import NoOptionError

from mmc.support.config import PluginConfig

class MscConfig(PluginConfig):

    def readConf(self):
        """
        Read the module configuration
        """
        PluginConfig.readConf(self)
        self.qactionspath = self.get("msc", "qactionspath")
        self.repopath = self.get("msc", "repopath")
        self.db_driver = self.get("msc", "db_driver")
        self.db_host = self.get("msc", "db_host")
        self.db_port = int(self.get("msc", "db_port"))
        self.db_name = self.get("msc", "db_name")
        self.db_user = self.get("msc", "db_user")
        self.db_passwd = self.get("msc", "db_passwd")
        try:
            self.db_debug = logging._levelNames[self.get("msc", "db_debug")]
        except NoOptionError:
            pass
        try:
            self.dbpoolrecycle = self.getint("msc", "db_pool_recycle")
        except NoOptionError:
            pass

        self.ma_server = self.get('package_api', 'mserver')
        self.ma_port = self.get('package_api', 'mport')
        self.ma_mountpoint = self.get('package_api', 'mmountpoint')

    def setDefault(self):
        """
        Set default values
        """
        PluginConfig.setDefault(self)
        self.db_debug = logging.ERROR
        self.dbpoolrecycle = 60

# static config ...
COMMAND_STATES_LIST = {
    "upload_in_progress":'',
    "upload_done":'',
    "upload_failed":'',
    "execution_in_progress":'',
    "execution_done":'',
    "execution_failed":'',
    "delete_in_progress":'',
    "delete_done":'',
    "delete_failed":'',
    "not_reachable":'',
    "done":'',
    "pause":'',
    "stop":'',
    "scheduled":''
}

UPLOADED_EXECUTED_DELETED_LIST = {
    "TODO":'',
    "IGNORED":'',
    "FAILED":'',
    "WORK_IN_PROGRESS":'',
    "DONE":''
}

COMMANDS_HISTORY_TABLE = 'commands_history'
COMMANDS_ON_HOST_TABLE = 'commands_on_host'
COMMANDS_TABLE = 'commands'
MAX_COMMAND_LAUNCHER_PROCESSUS = 50
CYGWIN_WINDOWS_ROOT_PATH = ''
MOUNT_EXPLORER = '/var/autofs/ssh/'
LINUX_SEPARATOR = '/'

MAX_LOG_SIZE = 15000

basedir = ''

config = { 'path_destination':'/', 'explorer':0 } # FIXME: to put in msc.ini


WINDOWS_SEPARATOR = "\\"
LINUX_SEPARATOR = "/"
S_IFDIR = 040000
MIME_UNKNOWN = "Unknown"
MIME_UNKNOWN_ICON = "unknown.png"
MIME_DIR = "Directory"
MIME_DIR_ICON = "folder.png"
DEFAULT_MIME = "application/octet-stream"

