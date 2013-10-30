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

import logging
from sqlalchemy.orm import create_session


class CommandsOnHostPhase(object):

    def flush(self):
        """ Handle SQL flushing """
        session = create_session()
        session.add(self)
        session.flush()
        session.close()
 
    def is_ready(self):
        return self.is_state("ready")
    def is_running(self):
        return self.is_state("running")
    def is_failed(self):
        return self.is_state("failed")
    def is_waiting(self):
        return self.is_state("waiting")
    def is_done(self):
        return self.is_state("done")

    def is_state(self, state):
        ret = self.state == state
        logging.getLogger().debug("is_state %s: %s" % (state, ret))
        return ret

    def switch_to_done(self):
        return self.switch_to("done")

    # TODO - reschedule ???
    def switch_to_failed(self):
        return self.switch_to("failed")
 
    def switch_to(self, state):
        if self.is_running():
            self.set_state(state)
            return True
        else:
            return False
        


    def set_ready(self):
        self.set_state("ready")

    def set_running(self):
        self.set_state("running")

    def set_failed(self):
        self.set_state("failed")

    def set_waiting(self):
        self.set_state("waiting")

    def set_done(self):
        self.set_state("done")

    def set_state(self, state):
        self.state = state
        logging.getLogger().debug("<%s> phase state: %s" % (self.name, state))
        self.flush()
 
