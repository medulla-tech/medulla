# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from pulse2.scheduler.types import Phase, DIRECTIVE
from pulse2.scheduler.utils import launcher_proxymethod


from pulse2.consts import PULSE2_SUCCESS_ERROR

class PullPhase(Phase):
    """Recurrent phase frame"""

    def perform(self):
        """ Perform the phase action. """
        return self.give_up()

    def give_up(self):
        """
        Encapsulates give-up directive.

        @return: give-up directive
        @rtype: DIRECTIVE
        """
        self.logger.debug("Circuit #%s: Releasing the recurrent phase" % self.coh.id)
        if self.coh.isStateStopped():
            return DIRECTIVE.STOPPED
        else :
            return DIRECTIVE.GIVE_UP

    def parse_pull_phase_result(self,(exitcode, stdout, stderr)):

        if exitcode == PULSE2_SUCCESS_ERROR: # success
            self.logger.info("Circuit #%s: pull %s done (exitcode == 0)" % (self.coh.id, self.name))
            self.update_history_done(exitcode, stdout, stderr)
            if self.coh.isStateStopped():
                return DIRECTIVE.KILLED

            if self.phase.switch_to_done():
                return self.next()
            return self.give_up()

        elif self.name in self.config.non_fatal_steps:
            self.logger.info("Circuit #%s: pull %s failed (exitcode != 0), but non fatal according to scheduler config file" % (self.coh.id, self.name))
            self.update_history_failed(exitcode, stdout, stderr)
            self.phase.set_done()
            return self.next()

        else: # failure: immediately give up
            self.logger.info("Circuit #%s: pull %s failed (exitcode != 0)" % (self.coh.id, self.name))
            self.update_history_failed(exitcode, stdout, stderr)
            return self.switch_phase_failed()




    def parse_pull_order(self, taken_in_account):
        self.parse_order(taken_in_account)

class WOLPhase(PullPhase):
    name = "wol"

    @launcher_proxymethod("pull_completed_wol")
    def parse_result(self, (exitcode, stdout, stderr)):
        return self.parse_pull_phase_result((exitcode, stdout, stderr))


class UploadPhase(PullPhase):
    name = "upload"

    @launcher_proxymethod("pull_completed_pull")
    def parse_result(self, (exitcode, stdout, stderr)):
        return self.parse_pull_phase_result((exitcode, stdout, stderr))


class ExecutionPhase(PullPhase):
    name = "execute"

    @launcher_proxymethod("pull_completed_exec")
    def parse_result(self, (exitcode, stdout, stderr)):
        return self.parse_pull_phase_result((exitcode, stdout, stderr))


class DeletePhase(PullPhase):
    name = "delete"

    @launcher_proxymethod("pull_completed_delete")
    def parse_result(self, (exitcode, stdout, stderr)):
        return self.parse_pull_phase_result((exitcode, stdout, stderr))


class InventoryPhase(PullPhase):
    name = "inventory"

    @launcher_proxymethod("pull_completed_inventory")
    def parse_result(self, (exitcode, stdout, stderr)):
        return self.parse_pull_phase_result((exitcode, stdout, stderr))


class RebootPhase(PullPhase):
    name = "reboot"

    @launcher_proxymethod("pull_completed_reboot")
    def parse_result(self, (exitcode, stdout, stderr)):
        return self.parse_pull_phase_result((exitcode, stdout, stderr))


class HaltPhase(PullPhase):
    name = "halt"

    @launcher_proxymethod("pull_completed_halt")
    def parse_result(self, (exitcode, stdout, stderr)):
        return self.parse_pull_phase_result((exitcode, stdout, stderr))
