# -*- coding: utf-8; -*-
#
# (c) 2014 Mandriva, http://www.mandriva.com/
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
