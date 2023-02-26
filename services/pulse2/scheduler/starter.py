# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

""" Dispatching of cyclic starts. """

import logging

from twisted.internet.threads import deferToThread
from twisted.internet.task import LoopingCall


class LoopingStarter(object):
    """
    Dispatching the batchs of start.

    Each circuit must be started in a separated thread and each launching
    must be delayed to avoid the saturation of launcher(s).
    """

    # looping call reference
    loop = None

    def __init__(self, dispatcher, emitting_period):
	"""
	@param dispatcher: main dispatcher reference
	@type dispatcher: MscDispatcher

	@param emitting_period: delay inserted among the starts
	@type emitting_period: float
	"""
	self.dispatcher = dispatcher
	self.emitting_period = emitting_period
	self.logger = logging.getLogger()


    def _run_one(self, circuit):
        """
        Executes the circuit in the thread.

        @param circuit: circuit to run
        @type circuit: Circuit

        @return: start result
        @rtype: Deferred
        """

        d = deferToThread(circuit.run)
        @d.addErrback
        def eb(reason):
	    """ Thread start fallback """
            self.logger.error("Circuit #%s: start failed: %s" % (circuit.id, reason))

        @d.addCallback
        def cb(reason):
	    """ Thread start callback """
            self.dispatcher._circuits.append(circuit)

        return d


    def _run_later(self, circuits):
        """
        Starts the each circuit with a predefined delay.

        This periodic call avoids a saturation on the server (i.e. launcher).
        @param circuits: circuits to start
        @type circuits: iterator
        """
        try :
            circuit = next(circuits)
            self._run_one(circuit)

        except StopIteration :
            if self.loop.running:
                self.loop.stop()

            self.logger.debug("circuits started")


    def run(self, circuits):
        """
        Executes all the circuits.

        @param circuits: circuits to run
        @type circuits: list

        @return: list of start results
        @rtype: list
        """
        try :
            if len(circuits) == 0:
                self.logger.info("Nothing to execute")
                return True

            self.loop = LoopingCall(self._run_later, iter(circuits))
            d = self.loop.start(self.emitting_period)
            d.addErrback(self._loop_fail)

	    return d

        except Exception, e :
            self.logger.error("Circuits start failed: %s" % str(e))
            return False

    def _loop_fail(self, failure):
	""" Looping call fallback """
        self.logger.error("Loop call starting failed: %s" % str(failure))

    def cancel(self):
        """ Interrupts immediatelly the looping calls """
        self.loop.stop()
