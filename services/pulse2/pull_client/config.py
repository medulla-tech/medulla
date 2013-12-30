# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Pulse Pull Client.
#
# Pulse Pull client is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse Pull Client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
import os
import logging
import inspect
from ConfigParser import ConfigParser, NoOptionError, NoSectionError

from utils import Singleton


logger = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


class PullClientConfig(Singleton):
    config = None

    class Service:
        name = "Pulse Pull Client"
        state_file = "results_cache.db"

    class Poller:
        wait_poll = 120
        poll_interval = 5
        result_workers = 1
        parallel_workers = 1

    class Dlp:
        client = "dlp.DlpClient"
        base_url = None
        authkey = "secret"
        hostname = ""
        mac_list = ""

    class Proxy:
        # override system proxy
        # eg: http://proxy.mandriva.com:3128/
        # or: http://user:password@proxy:3129/
        http= ""

    def __init__(self):
        location = os.path.dirname(os.path.abspath(__file__))
        # when compiled with cx_freeze configuration is outside
        # the python code
        if "library.zip" in location:
            location = os.path.dirname(location)
        self.Service.path = location
        self.config_file = os.path.join(location, "conf", "pull_client.conf")

        self.config = ConfigParser()
        self.config.read(self.config_file)
        for section, klass in inspect.getmembers(self, inspect.isclass):
            if section == "__class__":
                continue
            for attribute, default_value in inspect.getmembers(klass):
                if attribute.startswith("__"):
                    continue
                if type(default_value) == int:
                    method = 'getint'
                elif type(default_value) == bool:
                    method = 'getboolean'
                else:
                    method = 'get'
                try:
                    value = getattr(self.config, method)(section, attribute)
                    if type(default_value) == list:
                        value = [v.strip() for v in value.split(' ')]
                    setattr(getattr(self, section), attribute, value)
                except (NoSectionError, NoOptionError):
                    if default_value is None:
                        logger.error("%s missing from section %s" % (attribute, section))
                        raise ConfigError("%s missing from section %s" % (attribute, section))


NAME = "%s"
DISPLAY_NAME = "Pulse Pull Client (%s)"
MODULE_NAME = "service"
CLASS_NAME = "Handler"
DESCRIPTION = "Pulse service for Pull-mode deployment"
AUTO_START = True
