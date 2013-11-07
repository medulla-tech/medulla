# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
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
import time
import datetime

from twisted.internet.defer import DeferredList

from pulse2.utils import SingletonN

from pulse2.database.msc.orm.commands import Schedule

#from pulse2.scheduler.config import SchedulerConfig
from pulse2.scheduler.queries import get_phases
from pulse2.scheduler.api.msc import MscAPI

class Defaults(object):
    """ Gets and holds the default values from msc-plugin """
    __metaclass__ = SingletonN

    life_time = None
    attempts_per_day = None

    def setup(self):
        d1 = MscAPI().get_web_def_coh_life_time()
        d1.addCallback(self._set_life_time)

        d2 = MscAPI().get_web_def_attempts_per_day()
        d2.addCallback(self._set_attempts_per_day)

        return DeferredList([d1, d2])


    def _set_life_time(self, result):
        self.life_time = result

    def _set_attempts_per_day(self, result):
        self.attempts_per_day = result

defaults = Defaults()

class CleanUpSchedule :

    _checked_phase = "execute"
    _checked_status = "failed"

    _phases = ["wol", "delete", "done"]

    def __init__(self, ids):
        self.ids = ids

    def is_candidate(self):
        for phase in get_phases():
            if phase.name == self._checked_phase :
                if phase.state == self._checked_status :
                    return True
        return False

    def process(self):
        start_date, end_date = self._delta()

        schedule = Schedule(self.ids,
                            start_date,
                            end_date,
                            defaults.attempts_per_day,
                            self._phases
                            )
        schedule.create()
        

    def _delta (self):
        """ 
        Calculate of timedelta between new command start and end.

        @return: start and end date of rescheduled command
        @rtype: tuple
        """
        fmt = "%Y-%m-%d %H:%M:%S"
        
        start_timestamp = time.time()
        start_date = datetime.datetime.fromtimestamp(start_timestamp).strftime(fmt)
            
        delta = int(defaults.life_time) * 60 * 60
        end_timestamp = start_timestamp + delta
        end_date = datetime.datetime.fromtimestamp(end_timestamp).strftime(fmt)
      
        return start_date, end_date

        





 
