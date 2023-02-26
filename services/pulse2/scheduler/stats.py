# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

from twisted.internet import reactor

from pulse2.scheduler.queries import get_commands_stats, update_commands_stats
from pulse2.scheduler.queries import process_non_valid



class StatisticsProcessing :
    """
    Provides the periodical and final updates of global command statistics.

    Statistics are periodically updated to have a global sumarization
    of states of commands on host.

    Final statistics update is called on the last switching a circuit
    to overtimed state. This update is scheduled with a delay having
    the possibility to cancel if the previous updated circuit wasn't
    the last definitive circuit of updated command.
    """
    # global statistics container of valid commands
    stats = {}
    # scheduled final statistics updates
    wdogs = {}

    # previous commands (missing command == expired)
    previous = []


    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger()

    def update(self, cmd_id=None):
        """ Updates the global statistics or just for one command """
        if cmd_id :
            self.stats[cmd_id] = self._get_stats(cmd_id)[cmd_id]
        else:
            self.stats = self._get_stats()

        self.check_and_schedule_for_expired()

    def check_and_schedule_for_expired(self):
        """Looks for expired commands and schedules an update"""
        for cmd_id in self.previous :
            if cmd_id not in self.stats :
                # during previous awake presented, so now expired
                self.watchdog_schedule(cmd_id)

        self.previous = self.stats.keys()



    def _get_stats(self, cmd_id=None):
        """
        Looking for statistics for selected or all valid commands.

        @param cmd_id: id of Commands record
        @type cmd_id: int
        """
        __stats = get_commands_stats(self.config.name, cmd_id)

        stats = {}

        if cmd_id :
            all_states = dict([(q[1], q[2]) for q in __stats if q[0]==cmd_id])
            stats[cmd_id] = all_states
        else:
            cmd_ids = []
            [cmd_ids.append(k[0]) for k in __stats]

            for cmd_id in cmd_ids :
                all_states = dict([(q[1], q[2]) for q in __stats if q[0]==cmd_id])
                stats[cmd_id] = all_states

        return stats

    def _update_for(self, cmd_id):
        """
        Updates the global statistics of selected command

        @param cmd_id: id of Commands record
        @type cmd_id: int
        """
        try:
            process_non_valid(self.config.name,
                              self.config.non_fatal_steps)

            all_stats = self._get_stats(cmd_id)
            stats = all_stats[cmd_id]

            update_commands_stats(cmd_id, stats)


            del self.wdogs[cmd_id]
            self.logger.info("Final statistics updated for command: %s" % cmd_id)

        except Exception, e:
            self.logger.warn("Statistics update failed: %s" % str(e))

    def watchdog_schedule(self, cmd_id):
        """
        Schedules the final stats update.

        @param cmd_id: id of Commands record
        @type cmd_id: int
        """
        if cmd_id in self.wdogs :
            call_id = self.wdogs[cmd_id]
            call_id.cancel()
            self.logger.debug("Statistics: schedule cancelled: %s" % cmd_id)
        self.logger.debug("Statistics: scheduling the final update for command %s" % cmd_id)
        call_id = reactor.callLater(10, self._update_for, cmd_id)

        self.wdogs[cmd_id] = call_id
