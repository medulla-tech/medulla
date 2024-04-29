# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from sqlalchemy.orm import create_session


class CommandsOnHostPhase(object):
    def flush(self):
        """Handle SQL flushing"""
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

    def toDict(self, relations=False):
        d = self.__dict__
        if "_sa_instance_state" in d:
            del d["_sa_instance_state"]
        return d
