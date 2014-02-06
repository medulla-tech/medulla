# -*- coding: utf-8; -*-
#
# (c) 2014 Mandriva, http://www.mandriva.com/
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

""" Common id trackers related to circuits controled by MscDispatcher """

import time

class _Tracker(object):
    """ Abstract frame for trackers """

    ids = None

    def _append(self, id):
	""" Appends id into container """
	raise NotImplementedError

    def _remove(self, id):
	""" Removes id from container """
	raise NotImplementedError

    def __contains__(self, id):
        return id in self.ids

    def __len__(self):
        return len(self.ids)

    def add(self, ids):
        """
        Adds the circuits ids in the internal container.

        @param ids: circuits ids
        @type ids: list
        """
        for id in ids :
            if id not in self.ids:
		self._append(id)

    def remove(self, id):
        """
        Removes a circuit id.

        @param id: id of circuit
        @type ids: int
        """
        if id in self.ids:
            self._remove(id)
 

class Tracker(_Tracker):
    """ Simple circuits tracking. """

    ids = []

    def _append(self, id):
        """
        Adding the circuits ids.

        @param ids: circuits ids
        @type ids: list
        """
        self.ids.append(id)

    def _remove(self, id):
        """
        Removes a circuit id.

        @param id: circuit's identifier 
        @type id: int
        """
        self.ids.remove(id)



class TimedTracker(_Tracker):
    """ Tracking of circuits with timestamps. """

    ids = {}

    def __init__(self, life_time):
	self.life_time = life_time

    def update(self, id):
        self.ids[id] = time.time()

    def _append(self, id):
        self.ids[id] = time.time()


    def _remove(self, id):
        """
        Removes a circuit id with a timestamp.

        @param id: circuit's identifier 
        @type id: int
        """
	if id in self.ids:
	    del self.ids[id]

    def get_expired(self):

        now = time.time() 
	 
	return [id for (id, tp) in self.ids.items() if tp + self.life_time < now]

class StoppedTracker(Tracker):
    """Controls the stopped circuits """
    pass
 
class StartedTracker(TimedTracker):
    """Controls the running circuits with an expiration processing """
    pass
 



