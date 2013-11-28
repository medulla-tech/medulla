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
from datetime import datetime, timedelta

from pulse2.scheduler.balance import ParabolicBalance

class LaunchTimeResolver :

    now = None 
    start_date = None
    end_date = None
    attempts_failed = 0
    attempts_left = 0
    max_wol_time = 0
    deployment_intervals = ""
    intervals = []

    def __init__(self, **kwargs):

        #self.logger = logging.getLogger()
        for name, value in kwargs.items():
            if name not in dir(self) :
                raise AttributeError("Inexisting attribute: %s" % name)
            else :
                setattr(self, name, value)
        if not self.deployment_intervals:
            self.deployment_intervals = "0-0"
        self._set_intervals()

    @property
    def start_timestamp(self):
        """start date timestamp"""
        return time.mktime(self.start_date.timetuple())

    @property
    def end_timestamp(self):
        """end date timestamp"""
        return time.mktime(self.end_date.timetuple())

    @property
    def days_delta(self):
        """ number of days between start date and end_date"""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def attempts_total(self):
        """ Total of attempts for all days """
        return self.days_delta * self.attempts_left


    def get_valid_axe(self):
        """
        Creates a list of valid deployment intervals.

        @return: time axe of datetime intervals 
        @rtype: list
        """
        if not self.deployment_intervals :
            return [(self.start_date, self.end_date)]
        axe = []

        start_date = self.start_date
    
        while True :
            if start_date > self.end_date :
                break
            for start_hour, end_hour in self.intervals :
                start = datetime(year=start_date.year, 
                                 month=start_date.month,
                                 day=start_date.day,
                                 hour=start_hour)

                end = datetime(year=start_date.year, 
                               month=start_date.month,
                               day=start_date.day,
                               hour=end_hour)
                if end_hour == 0 :
                    end += timedelta(days=1)

                if start < self.start_date :
                    start = self.start_date
                if end > self.end_date :
                    end = self.end_date

                if end < self.start_date :
                    continue
                if start > self.end_date : 
                    break

                
                axe.append((start, end))

            midnight = datetime(year=start_date.year, 
                                month=start_date.month,
                                day=start_date.day)
 
            start_date = midnight + timedelta(days=1)
            
        return axe

         

    def get_total_valid_time(self):
        """
        Pure deployment time in seconds during the valid intervals

        @return: deployment duration
        @rtype: int
        """
        return sum([(end-start).seconds for (start, end) in self.get_valid_axe()])

    def get_milestone_stamps(self):
        """
        Returns a list of relative timestamps starting from start_date
        during the valid period.

        @return: list of timestamps
        @rtype: list
        """
        stamps = []
        seconds = 0
        for (start, end) in self.get_valid_axe():
            period_total = (end-start).seconds
            seconds += period_total
            stamps.append(seconds)
        return stamps


    def get_launch_date(self):
        """ 
        Detects a valid date for the next command launch.

        @return: next launch date
        @rtype: datetime
        """
        if self.attempts_failed + 1 <= self.attempts_total :
            b = ParabolicBalance(self.attempts_total)
            delay = 0
            for i in range(self.attempts_failed):
                coef = b.balances[i] * 1.0
                delta = int(coef * self.get_total_valid_time())
                delay += delta
            return self._get_date(delay)
 
    def _get_date(self, delay):
        """
        Applying the calculated delay on milestone pattern.

        @param delay: relative delay (excluding invalid periods)
        @type delay: int

        @return: valid launch date
        @rtype: datetime
        """        
        previous = 0
        for i, stamp in enumerate(self.get_milestone_stamps()):
            if delay in range(previous, stamp):
                start, end = self.get_valid_axe()[i]
                delta = delay - previous
                return start + timedelta(seconds=delta)

            previous = stamp

    def _set_intervals(self):
        """Extracts the intervals from string to the list of tuples"""
        self.intervals = self.extract_intervals(self.deployment_intervals)

    @classmethod 
    def extract_intervals(cls, deployment_intervals):
        """Extracts the intervals from string to the list of tuples"""
        intervals = []
        for segment in deployment_intervals.split(','):
            unit = segment.split('-')
            if len(unit) == 2:
                (start, end) = [int(d) for d in unit]
                if start >= end and end != 0:
                    raise ValueError("<start> must be less than to <end>")
                intervals.append((start, end))
        return intervals

    @classmethod
    def in_deployment_interval(cls, deployment_intervals, launch_date):

        intervals = cls.extract_intervals(deployment_intervals)
        for start, end in intervals :
            if launch_date.hour >= start and launch_date.hour < end:
                return True
        return False


    def get_execution_plan(self):
        """Returns all possibles launch dates durring the command validity"""
        exec_dates = []

        b = ParabolicBalance(self.attempts_total)
        delay = 0
        for i in range(self.attempts_failed):
            coef = b.balances[i] * 1.0
            delta = int(coef * self.get_total_valid_time())
            delay += delta
            exec_dates.append(self._get_date(delay))

        return exec_dates


