#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
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
    Store proxies usage (usefull to limit proxy usage)
"""

# semaphore handling
import threading

# entripy stuff
import random

# Others Pulse2 Stuff
import pulse2.utils

class LocalProxiesUsageTracking(pulse2.utils.Singleton):

    # proxies structure, dict
    # keys are the proxyes UUID
    # each item beeing:
    #   "current_client_number" => int
    #   "max_client_number" => int
    #   "current_commands", dict,
    #   keys are the command_id
    #   each item beeing:
    #     "current_client_number" => int
    #     "max_client_number" => int
    proxies = dict()    # internal structure

    # access semaphore
    # /!\: by CONVENTION, ONLY PUBLIC FUNCTIONS DO TAKE LOCK
    semaphore = threading.Semaphore(1)

    def __repr__(self):
        return self.proxies.__repr__()

    def __lock(self):
        # commented: should work without it !
        # self.semaphore.acquire(True)
        pass

    def __unlock(self):
        # commented: should work without it !
        # self.semaphore.release()
        pass

    def __create_proxy(self, uuid):
        """ create proxy dict if it do not exists """
        if not uuid in self.proxies:
            self.proxies[uuid] = dict()

    def __create_command(self, uuid, max_client_number, command_id):
        """ create command sub-dict if it do not exists """
        self.__create_proxy(uuid)
        if not command_id in self.proxies[uuid]:
            self.proxies[uuid][command_id] = {
                "max_client_number": max_client_number,
                "current_client_number": 0
            }

    def __get_free_proxies_for_command(self, command_id):
        """ return a list of free proxy for a given command """
        ret = list()
        for uuid in self.proxies:
            if command_id in self.proxies[uuid]:
                if self.proxies[uuid][command_id]["current_client_number"] < self.proxies[uuid][command_id]["max_client_number"]:
                    ret.append(uuid)
        return ret

    def __increment_usage(self, uuid, command_id):
        """ attempt to increment usage of a proxy for a given command """
        if self.proxies[uuid][command_id]["current_client_number"] < self.proxies[uuid][command_id]["max_client_number"]:
            self.proxies[uuid][command_id]["current_client_number"] += 1
            return True
        else:
            return False

    def __decrement_usage(self, uuid, command_id):
        """ attempt to decrement usage of a proxy for a given command """
        if uuid in self.proxies:
            if command_id in self.proxies[uuid]:
                self.proxies[uuid][command_id]["current_client_number"] -= 1
                if self.proxies[uuid][command_id]["current_client_number"] < 0: # well, should not append
                    self.proxies[uuid][command_id]["current_client_number"] = 0

    def take(self, uuid, max_client_number, command_id):
        """ create and take lock for a given command on a given proxy """
        self.__lock()
        self.__create_command(uuid, max_client_number, command_id)
        ret = self.__increment_usage(uuid, command_id)
        self.__unlock()
        return ret

    def how_much_left_for(self, uuid, command_id):
        """ create and take lock for a given command on a given proxy """
        ret = 0
        if uuid in self.proxies:
            if command_id in self.proxies[uuid]:
                cur = self.proxies[uuid][command_id]["current_client_number"]
                max = self.proxies[uuid][command_id]["max_client_number"]
                ret = max - cur
        return ret

    def untake(self, uuid, command_id):
        """ release lock for a given command on a given proxy """
        # FIXME: we should destroy the struct if empty
        self.__lock()
        self.__decrement_usage(uuid, command_id)
        self.__unlock()

    def take_one(self, candidates, command_id):
        """ return a candidate in uuids for given command """
        result = False
        self.__lock()
        # alway create structures
        for (uuid, max_client_number) in candidates:
            self.__create_command(uuid, max_client_number, command_id)
        free_proxies = self.__get_free_proxies_for_command(command_id)
        if len(free_proxies) > 0:
            final_proxy = free_proxies[random.randint(0, len(free_proxies)-1)]
            result = self.__increment_usage(final_proxy, command_id)
        self.__unlock()
        if result:
            return final_proxy
        return result

