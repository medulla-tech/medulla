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

""" A proxy to MSC methods """

import time
import datetime
import logging

from pulse2.scheduler.api.mmc_client import RPCClient


log = logging.getLogger()

class MscAPI(RPCClient):
    """ XMLRPC Proxy trough MMC agent to accessing MSC methods. """

    def errorback(self, failure):
        """ Common errorback of XMLRPC calls"""
        log.warn("MscAPI: %s" % str(failure))

    def get_web_def_coh_life_time(self):
        """ Getting of default lifetime of command """

        fnc = "msc.get_web_def_coh_life_time"

        d = self.rpc_execute(fnc)
        d.addErrback(self.errorback)
        return d

    def get_web_def_attempts_per_day(self):
        """ Default number of daily attempts """

        fnc = "msc.get_web_def_attempts_per_day"

        d = self.rpc_execute(fnc)
        d.addErrback(self.errorback)
        return d


class CoHTimeExtend(MscAPI):
    """ Get the time interval of new rescheduled delete command """

    def get_deferred(self):
        """ Time interval deferred getter """
        d = self.get_web_def_coh_life_time()
        d.addCallback(self.send_result)
        return d


    def send_result(self, result):
        """ Callback of XMLRPC getter """
        return self._delta(result)


    def _delta (self, coh_life_time):
        """ 
        Calculate of timedelta between new command start and end.

        @param coh_life_time: default life time of command
        @type coh_life_time: int

        @return: start and end date of rescheduled command
        @rtype: tuple
        """
        fmt = "%Y-%m-%d %H:%M:%S"
        
        start_timestamp = time.time()
        start_date = datetime.datetime.fromtimestamp(start_timestamp).strftime(fmt)
            
        delta = int(coh_life_time) * 60 * 60
        end_timestamp = start_timestamp + delta
        end_date = datetime.datetime.fromtimestamp(end_timestamp).strftime(fmt)
      
        return start_date, end_date

