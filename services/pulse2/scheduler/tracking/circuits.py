# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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
