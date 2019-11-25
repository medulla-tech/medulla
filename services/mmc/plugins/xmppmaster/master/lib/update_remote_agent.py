# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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
# File xmppmaster/master/lib/update_remote_agent.py
#
import hashlib
import os
import logging
from utils import file_get_contents
import json


class Update_Remote_Agent:
    """
        this class make finderspring of agent.
        Param : dir_agent_base is location of agent
        Param : autoupdate is switch for enable or disable remote update.
    """

    def __init__(self, dir_agent_base, autoupdate=True):
        self.dir_agent_base = dir_agent_base
        self.autoupdate = autoupdate
        self.directory = {"program_agent": {},
                          "version": "",
                          "version_agent": "",
                          "lib_agent": {},
                          "script_agent": {},
                          "fingerprint": ""}
        # verify exist dir and create si not exit. The default mode is 0777 (octal)
        dir_create = [dir_agent_base,
                      os.path.join(dir_agent_base, 'lib'),
                      os.path.join(dir_agent_base, 'script')]
        for path_dir_remoteagent in dir_create:
            if not os.path.exists(path_dir_remoteagent):
                os.makedirs(path_dir_remoteagent)
                logging.getLogger().debug("Creating folder for remote base agent : %s" % dir_agent_base)
        if os.path.exists(os.path.join(dir_agent_base, 'agentversion')):
            self.load_list_md5_agentbase()

    def get_md5_descriptor_agent(self):
        return self.directory

    def md5_descriptor_agent_to_string(self):
        return json.dumps(self.get_md5_descriptor_agent(), indent=4)

    def get_fingerprint_agent_base(self):
        return self.directory["fingerprint"]

    def load_list_md5_agentbase(self):
        listmd5 = []
        self.directory = {"program_agent": {},
                          "version": "",
                          "version_agent": "",
                          "lib_agent": {},
                          "script_agent": {},
                          "fingerprint": ""}
        self.directory["version"] = file_get_contents(
            os.path.join(self.dir_agent_base, 'agentversion'))
        self.directory["version_agent"] = hashlib.md5(self.directory["version"]).hexdigest()
        listmd5.append(self.directory["version_agent"])
        list_script_python_for_update = ['agentxmpp.py', 'launcher.py', 'connectionagent.py', 'replicator.py']

        # for fichiername in [ x for x in os.listdir(self.dir_agent_base) if x[-3:]== ".py"]:
        for fichiername in list_script_python_for_update:
            self.directory["program_agent"][fichiername] = hashlib.md5(
                file_get_contents(os.path.join(self.dir_agent_base, fichiername))).hexdigest()
            listmd5.append(self.directory["program_agent"][fichiername])
        for fichiername in [x for x in os.listdir(os.path.join(self.dir_agent_base, 'lib')) if x[-3:] == ".py"]:
            self.directory["lib_agent"][fichiername] = hashlib.md5(file_get_contents(
                os.path.join(self.dir_agent_base, 'lib', fichiername))).hexdigest()
            listmd5.append(self.directory["lib_agent"][fichiername])
        for fichiername in [x for x in os.listdir(os.path.join(self.dir_agent_base, 'script')) if x[-4:] == ".ps1"]:
            self.directory["script_agent"][fichiername] = hashlib.md5(file_get_contents(
                os.path.join(self.dir_agent_base, 'script', fichiername))).hexdigest()
            listmd5.append(self.directory["script_agent"][fichiername])
        listmd5.sort()
        self.directory["fingerprint"] = hashlib.md5(json.dumps(listmd5)).hexdigest()
