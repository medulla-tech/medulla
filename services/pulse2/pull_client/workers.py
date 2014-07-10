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
import os
import time
import logging
import Queue
from threading import Thread

from datetime import datetime

from command import CommandFailed
from launcher import launcher


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

    def __init__(self, stop, step_queue, result_queue, watchdog_queue, **kwargs):
        Thread.__init__(self, **kwargs)
        self.stop = stop
        self.step_queue = step_queue
        self.result_queue = result_queue
        self.watchdog_queue = watchdog_queue

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
                    self.watchdog_queue.put(time.time())
                else:
                    result = step.start()
                    if result.send:
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
                        self.watchdog_queue.put(time.time())
                self.step_queue.task_done()
        logger.debug("Exiting from %s" % self)

class WatchdogWorker(Thread):

    scheduled_to = None

    def __init__(self, stop, queue, queues,
                 post_deploy_script, triggers_folder, **kwargs):
        Thread.__init__(self, **kwargs)
        self.stop = stop
        self.queue = queue
        self.queues = queues
        self.post_deploy_script = post_deploy_script
        self.triggers_folder = triggers_folder

        self.checkout()


    def run(self):
        logger.debug("%s running" % self)
        while not self.stop.is_set():
            try:
                # gets the timestamp of  expiration
                self.scheduled_to = self.queue.get(False)
            except Queue.Empty:
                # waiting for next run
                self.stop.wait(10)
            else:
                self.queue.task_done()

            self.checkout()

        logger.debug("Exiting from %s" % self)

    def checkout(self):
        if not self.scheduled_to is None:
            now = time.time()
            time.sleep(30)
            logger.debug("Re-lock scheduled to %s" % datetime.fromtimestamp(self.scheduled_to).strftime("'%Y-%m-%d %H:%M:%S'"))
            if now > self.scheduled_to and self.queues.empty():
                logger.info("Watchdog timeout reached")
                self._execute()
            elif self.queues.empty():
                logger.info("All commands finished, locking")
                self._execute()


    def _execute(self):

        logger.info("Watchdog - re-locking the access !")

        if not uwf_locked():
            logger.info("\033[31mMachine lock\033[0m")
            self.scheduled_to = None


        cmd_lock = "uwfmgr.exe filter enable"
        cmd_reboot = "/bin/shutdown.exe -r now"

        for cmd in [cmd_lock, cmd_reboot]:
            try:
                output, exitcode = launcher(cmd, '', None)
                logger.debug("Output of command '%s' : %s" % (cmd, output))
            except Exception, e:
                logger.error("Execution ofCommand '%s' failed: %s" % (cmd, str(e)))
        return True



def uwf_locked():
    temp_file = "/tmp/toto"
    path = "uwfmgr.exe get-config > %s" % temp_file
    try:
        output, exitcode = launcher(path, '', None)
        logger.info("UWF check: %s" % output)
        #pass
    except Exception, e:
        logger.error("UWF check error: %s" % e)
    else:

        path = os.path.join("C:/",
                            "Program Files",
                            "Mandriva",
                            "OpenSSH",
                            "tmp",
                            "toto")

        logger.info("UWF toto path: %s" % path)
        try:
            buff = []
            with open(path, "rb") as f:
                while True:
                    segment = f.read(1)
                    if not segment:
                        break
                    if ord(segment)==0:
                        continue
                    char = chr(ord(segment))

                    buff.append(char)
            for line in "".join(buff).split("\n"):
                if "Filter state" in line:
                    if "ON" in line:
                        logger.debug("UWF state: \033[31mLOCKED\033[0m")
                        return True
                    if "OFF" in line:
                        logger.debug("UWF state: \033[32mUNLOCKED\033[0m")
                        return False
            else:
                logger.error("UWF state can't be checked")
                return True
        except Exception, e:
            logger.error("UWF check tmp error: %s" % e)



