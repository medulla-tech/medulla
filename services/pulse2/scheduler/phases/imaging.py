# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from pulse2.scheduler.types import Phase
from pulse2.scheduler.api.imaging import ImagingAPI
from pulse2.consts import PULSE2_UNKNOWN_ERROR



class ImagingRpcPhase(Phase):
    rpc_method_name = None

    def _get_rpc_method_args(self):
        return self.target.target_uuid, self.target.target_name


    def perform(self):
        try :
            method = getattr(ImagingAPI(), self.rpc_method_name)
            args = self._get_rpc_method_args()

            d = method(*args)

            d.addCallback(self.parse_imaging_rpc_result)
            d.addErrback(self.parse_imaging_rpc_error)

            return d
        except Exception, e:
            self.logger.error("Circuit #%s: imaging phase failed: %s" % (self.coh.id, str(e)))

    def parse_imaging_rpc_result(self, result):

        if result :
            self.update_history_done()
            if self.phase.switch_to_done():
                self.coh.setStateScheduled()
                return self.next()
        else :
            self.logger.info("Circuit #%s: %s phase failed (exitcode != 0)" % (self.coh.id, self.name))
            self.update_history_failed()

            if not self.phase.switch_to_failed():
                return self.failed()
            return self.give_up()

    def parse_imaging_rpc_error(self, reason):
        self.logger.warn("Circuit #%s: %s phase failed, unattented reason: %s" %
                (self.name, self.coh.id, reason.getErrorMessage()))
        self.update_history_failed(PULSE2_UNKNOWN_ERROR,
                                   '',
                                   reason.getErrorMessage()
                                  )
        return self.switch_phase_failed()

class PreImagingMenuPhase(ImagingRpcPhase):
    name = "pre_menu"
    rpc_method_name = "setWOLMenu"

class PostImagingMenuPhase(ImagingRpcPhase):
    name = "post_menu"
    rpc_method_name = "unsetWOLMenu"
