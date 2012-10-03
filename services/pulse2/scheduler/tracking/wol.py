#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2009 Mandriva, http://www.mandriva.com/
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
    Store WOL locking stuff

    The idea is that as a WOL operation can take some time
    (5 minutes by default), we have to store somewhere that
    the WOL operation is still in progress; historically
    we relay on a timed callback to do this (plus timestamp
    storage in database to survive to a service restart),
    but this is not as efficient as we first though : if
    the WOL request takes more than 5 minutes to return,
    the command can be performed in parallel, leading to
    a locked command.

    In "standard" exploitation conditions, the following workflow is be used:
     - if WOL is "TODO" : do it
     - if WOL is in progress: check the timestamp :
       - if less than 5 minutes, give up (still running)
       - if more than 5 minutes, assumes that the scheduler was restarted; set it to "DONE" and jump to upload phase
     - WOL stage set to "IN PROGRESS"
     - WOL timestamp set in database
     - WOL asked
       + success : WOL waiting (5 minutes) +  WOL stage set to "DONE" + jump to upload phase
       + failure : WOL timestamp unset in database + WOL stage set to "TODO" + give up

    The flaw is if the WOL request takes longer than 5 minutes, we can fall into
    the following situation :
    - one iteration where the scheduler thinks it has been restared, set the WOL status to "DONE" and starts to upload
    - and one iteration when the WOL "suddently" returns, and either set WOL to DONE and upload, or set WOL to FAILED
    => two parallel executions

    this singleton is used to prevent this :
    - the initial WOL locks the command
    - when the callback returns, the lock is released
    - the upload phase checks if :
      1/ the command should have done a WOL
      2/ if (and when) the WOL has been asked
      3/ if the WOL is locked for this operation



"""

# semaphore handling
import threading

# logging stuff
import logging

# Others Pulse2 Stuff
import pulse2.utils

class WOLTracking(pulse2.utils.Singleton):

    # commands_on_host structure, dict
    # keys are the commands_on_host Ids
    # each item beeing:
    #   "timestamp" => int
    coh = dict()    # internal structure

    semaphore = threading.Semaphore(1)

    def __lock(self):
        self.semaphore.acquire(True)

    def __unlock(self):
        self.semaphore.release()

    def __repr__(self):
        return self.coh.__repr__()

    def __lock_coh(self, id):
        """
            return True if coh has been created
            return False if already exists
        """
        if not id in self.coh:
            self.coh[id] = True
            return True
        else:
            return False

    def __locked_coh(self, id):
        """
            return True if already exists
            return False if do not exists
        """
        if id in self.coh:
            return True
        else:
            return False

    def __unlock_coh(self, id):
        """
            return True if coh has been deleted
            return False if it did not exists
        """
        if id in self.coh:
            del self.coh[id]
            return True
        else:
            return False

    def lockwol(self, id):
        """ create and take lock for a given coh """
        self.__lock()
        ret = self.__lock_coh(id)
        if not ret:
            logging.getLogger().warn('LOCK: KO to lock WOL #%s' % (id))
        self.__unlock()
        return ret

    def iswollocked(self, id):
        """ see if there is a lock for a given coh """
        ret = self.__locked_coh(id)
        if not ret:
            logging.getLogger().warn('LOCK: WOL #%s not locked' % (id))
        else:
            logging.getLogger().warn('LOCK: WOL #%s is locked' % (id))
        return ret

    def unlockwol(self, id):
        """ release lock for a given coh """
        self.__lock()
        ret = self.__unlock_coh(id)
        if not ret: # not an error, as can be called after an xmlrpc command
            logging.getLogger().warn('LOCK: KO to unlock WOL #%s' % (id))
        self.__unlock()
        return ret
