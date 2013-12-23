# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Pulse Pull Client.
#
# Pulse Pull client is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse Pull Client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
import logging
import Queue
from threading import Thread


from command import CommandFailed


logger = logging.getLogger(__name__)


class ResultWorker(Thread):

    def __init__(self, stop, start_polling, result_queue, retry_queue, dlp_client, **kwargs):
        Thread.__init__(self, **kwargs)
        self.stop = stop
        self.start_polling = start_polling
        self.result_queue = result_queue
        self.retry_queue = retry_queue
        self.dlp_client = dlp_client
        self.retry_timeout = 20

    def run(self):
        logger.debug("%s running" % self)
        while not self.stop.is_set():
            try:
                # Check if there is some result
                # to re send first.
                # We want to send the results in
                # the same order as the execution
                if not self.retry_queue.empty():
                    queue = self.retry_queue
                # Nothing to re-send, get a new
                # result
                else:
                    queue = self.result_queue
                result = queue.get(False)
            except Queue.Empty:
                # When results queues are empty
                # we want to poll the DLP
                self.start_polling.set()
                # Nothing to do
                # Waiting for new result...
                self.stop.wait(10)
            else:
                # Error while sending the result
                if not self.dlp_client.send_result(result):
                    self.retry_queue.put(result)
                    # Wait a little before retrying
                    self.stop.wait(self.retry_timeout)
                queue.task_done()
        logger.debug("Exiting from %s" % self)


class StepWorker(Thread):

    def __init__(self, stop, step_queue, result_queue, **kwargs):
        Thread.__init__(self, **kwargs)
        self.stop = stop
        self.step_queue = step_queue
        self.result_queue = result_queue

    def run(self):
        logger.debug("%s running" % self)
        while not self.stop.is_set():
            try:
                step = self.step_queue.get(False)
            except Queue.Empty:
                # Waiting for new step...
                self.stop.wait(10)
            else:
                try:
                    step.can_run()
                except CommandFailed:
                    # Command is failed, forget step
                    # Should not happen
                    pass
                else:
                    result = step.start()
                    self.result_queue.put(result)
                    logger.debug(result)
                    if result.is_success or not step.required:
                        # If the step is not required (in non_fatal_steps)
                        # continue as if the step result is a success
                        step.command.next_step()
                    else:
                        # If step failed command is marked as failed
                        # and we wait to poll the command again
                        # from the scheduler
                        step.command.failed = True
                        logger.error("%s failed." % step.command)
                self.step_queue.task_done()
        logger.debug("Exiting from %s" % self)
