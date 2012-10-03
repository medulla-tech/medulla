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
    Store commands locking

    commands can be preempted from two sources:
    - the scheduler itself, when starting a command,
    - by XMLRPC request from a launcher

    commands are released when the scheduler gives up

    Locks are granted even if command is already locked, if lock is older
    than max_age.
"""

# semaphore handling
import threading

# time stuff
import time

# logging stuff
import logging

# Others Pulse2 Stuff
import pulse2.utils

class CommandsOnHostTracking(pulse2.utils.Singleton):

    # commands_on_host structure, dict
    # keys are the commands_on_host Ids
    # each item beeing:
    #   "timestamp" => int
    coh = dict()    # internal structure

    # access semaphore
    # /!\: by CONVENTION, ONLY PUBLIC FUNCTIONS DO TAKE LOCK
    semaphore = threading.Semaphore(1)

    # lock is time-base : released if lock older than N seconds
    max_age = 3600

    def __repr__(self):
        return self.coh.__repr__()

    def __lock(self):
        # commented: should work without it !
        # self.semaphore.acquire(True)
        pass

    def __unlock(self):
        # commented: should work without it !
        # self.semaphore.release()
        pass

    def __lock_coh(self, id):
        """
            create proxy dict if it do not exists
            return epoch if coh has been created
            return False if already exists
        """
        if not id in self.coh:
            epoch = time.time()
            self.coh[id] = {
                'timestamp': epoch
            }
            return epoch
        else:
            epoch = time.time()
            age = epoch - self.coh[id]['timestamp']
            # renew lock of lock was too old
            if age > self.max_age :
                self.coh[id] = {
                    'timestamp': epoch
                }
                return epoch
            else:
                return False

    def __unlock_coh(self, id):
        """
            delete proxy dict if it exists
            return epoch if coh has been deleted
            return False if it did not exists
        """
        if id in self.coh:
            epoch = self.coh[id]['timestamp']
            del self.coh[id]
            return epoch
        else:
            return False

    def __get_coh_age(self, id):
        if id in self.coh:
            return time.time() - self.coh[id]['timestamp']
        else:
            return False

    def preempt(self, id):
        """ create and take lock for a given coh """
        self.__lock()
        ret = self.__lock_coh(id)
        if not ret:
            logging.getLogger().warn('LOCK: KO for preempting #%s' % (id))
        self.__unlock()
        return ret

    def release(self, id):
        """ release lock for a given coh """
        self.__lock()
        epoch = time.time()
        ret = self.__unlock_coh(id)
        if not ret: # not an error, as can be called after an xmlrpc command
            logging.getLogger().warn('LOCK: KO for releasing #%s (was not locked), releasing anyway' % (id))
        self.__unlock()
        return ret
