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
        return self.switch_phase_failed(False)

class PreImagingMenuPhase(ImagingRpcPhase):
    name = "pre_menu"
    rpc_method_name = "setWOLMenu"

class PostImagingMenuPhase(ImagingRpcPhase):
    name = "post_menu"
    rpc_method_name = "unsetWOLMenu"


