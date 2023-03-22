# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

""" Testing of scheduler's basetypes. """

import logging
import unittest
logging.basicConfig()

#from twisted.trial import unittest

from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred

from pulse2.scheduler.types import Phase, Circuit, DIRECTIVE
from pulse2.scheduler.utils import launcher_proxymethod


from pulse2.scheduler.tests.tools import TableFactory


class CoHQueryFrame(object):
    """
    Simulates a CoHQuery instance.

    TableFactory ensures the mapping of all needed attributes
    and can be controlled by the methods inherited from ORM classes.
    """

    __metaclass__ = TableFactory

    def get_phase(self, name):
        return self.phase

    def get_phases(self):
        return ["exec", "del"]




class _MyPhase(Phase):
    """To avoid some DB r/w operations, we must simplify some routines"""

    def set_cohq(self, cohq):
        """Overriden CoHQuery setter to avoid TypeError exception raise."""
        self.coh = cohq.coh
        self.cmd = cohq.cmd
        self.target = cohq.target

        self.phase = cohq.get_phase(self.name)

    def _apply_initial_rules(self):
        return DIRECTIVE.PERFORM

    def _switch_on(self):
        return DIRECTIVE.PERFORM

    def run(self):
        return DIRECTIVE.NEXT



class ExecPhase(_MyPhase):
    name = "exec"
    @launcher_proxymethod("completed_01")
    def proxymethod01(self):
        pass


class DelPhase(_MyPhase):
    name = "del"
    @launcher_proxymethod("completed_02")
    def proxymethod02(self):
        pass

class DonePhase(_MyPhase):
    name = "done"

class MyCircuit(Circuit):
    def __init__(self, _id, installed_phases, config):
        self.logger = logging.getLogger()
        self.id = _id
        self.config = config

        self.cohq = CoHQueryFrame()
        self.cohq.cmd.id = 1
        self.cohq.coh.id = 1
        self.cohq.target.target_ipaddr = "55.12.120.83||127.0.0.1"
        self.cmd_id = self.cohq.cmd.id

        self.installed_phases = installed_phases



class TestPhases(unittest.TestCase):
    def setUp(self):
        cohq = CoHQueryFrame()
        cohq.cmd.id = 1
        cohq.coh.id = 1
        cohq.target.target_ipaddr = "55.12.120.83||127.0.0.1"
        self.phase1 = ExecPhase(cohq, "55.12.120.83", None)

        cohq = CoHQueryFrame()
        cohq.cmd.id = 2
        cohq.coh.id = 2
        self.phase2 = DelPhase(cohq, "55.12.120.84", None)

    def test_proxymethods(self):
        self.assertTrue("completed_01" in self.phase1.proxy_methods)
        self.assertFalse("completed_001" in self.phase1.proxy_methods)
        self.assertTrue("completed_02" in self.phase2.proxy_methods)
        self.assertFalse("completed_0020" in self.phase2.proxy_methods)


class TestCircuit(unittest.TestCase):

    def setUp(self):
        from pulse2.scheduler.config import SchedulerConfig
        config = SchedulerConfig()
        config.setup("/etc/mmc/pulse2/scheduler/scheduler.ini")

        installed_phases = [ExecPhase, DelPhase, DonePhase]

        self.circuit = MyCircuit(1, installed_phases, config)
        self.circuit.cohq.cmd.id = 1
        self.circuit.cohq.coh.id = 1
        self.circuit.cohq.target.target_name = "my_hostname"
        self.circuit.cohq.target.target_ipaddr = "55.12.120.83||127.0.0.1"
        self.circuit.cohq.target.target_macaddr = "00:01:00:52:2d:01||00:01:00:52:2d:01"

        self.circuit.cohq.target.target_network = "255.255.0.0||255.0.0.0"

        # some needed objects
        class Statistics (object):
            stats = []
            def update(cls, id) :pass

        dispatcher = type("MscContainer",
                          (object,),
                          {"release": lambda x : x,
                           "statistics" : Statistics()
                                                     })
        self.circuit.install_dispatcher(dispatcher)

    def test01_circuit_setup(self):
        def check(result):
            self.assertEqual(self.circuit, result)

        d = self.circuit.setup()
        d.addCallback(check)
        @d.addErrback
        def eb(failure):
            print "Test circuit setup failed: %s" % failure

    def test02_circuit_to_last_phase(self):
        """Circuit running with a simply workflow"""
        def setup(result):
            dr = maybeDeferred(self.circuit.run)
            return dr
        def check(result):
            # added a little lag to wait to last phase
            reactor.callLater(1, self.assertEqual, self.circuit.running_phase, DonePhase)

        d = self.circuit.setup()
        d.addCallback(setup)
        d.addCallback(check)
        @d.addErrback
        def eb(failure):
            print "Test circuit setup failed: %s" % failure



if __name__ == "__main__":

    unittest.main()
