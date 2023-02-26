# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""A simple unittest of looping start of circuits."""

import logging
logging.basicConfig()

from twisted.trial import unittest

from pulse2.scheduler.starter import LoopingStarter


class Circuit (object):
    """A simple Circuit object having needed atributtes"""

    id = None
    # flag to indicate a started circuit
    started = False

    def __init__(self, id):
	self.id = id


    def run(self):
	self.started = True
	return True


class Test00_LoopingStart(unittest.TestCase):

    def setUp(self):
	self.logger = logging.getLogger()
        self.dispatcher = type("MscDispatcher",
			      (object,),
			      {"_circuits": []}
			       )
	self.circuits = []
	for id in xrange(10):
	    self.circuits.append(Circuit(id))

	self.starter = LoopingStarter(self.dispatcher,
	                              0.2)


    def test01_start(self):
	"""Start of looping start """

	return self.starter.run(self.circuits)

    def test02_result(self):
	"""Checks if all circuits has been started"""
        result = all([c.started for c in self.dispatcher._circuits])
        self.assertTrue(result)
