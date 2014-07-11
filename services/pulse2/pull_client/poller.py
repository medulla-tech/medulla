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
import pickle
import importlib
from threading import Thread, Event
from Queue import Queue
from subprocess import Popen, PIPE

from command import Command
from workers import WatchdogWorker, ResultWorker, StepWorker
from config import PullClientConfig
from launcher import launcher


logger = logging.getLogger(__name__)


class QueueFinished(object):
    pass

class QueuesContainer(object):
    queues = []

    def add(self, queue):
        self.queues.append(queue)

    def empty(self):
        for queue in self.queues:
            if not queue.empty():
                return False
        return True


class Poller(Thread):
    commands = []
    workers = []
    last_update_ts = None

    def __init__(self, stop, **kwargs):
        Thread.__init__(self, **kwargs)
        # Get config
        self.config = PullClientConfig.instance()
        # Results state cache
        self.state_path = os.path.join(self.config.Service.path,
                                       self.config.Service.state_file)
        # Instantiate DLP client
        mod_name, class_name = self.config.Dlp.client.rsplit('.', 1)
        module = importlib.import_module(mod_name)
        self.dlp_client = getattr(module, class_name)()
        # stop event for stopping the DLP poller
        self.stop = stop
        self.stop_workers = Event()
        self.start_polling = Event()
        # queues for workers
        # self.parallel_queue: wol, upload, delete steps
        # self.simple_queue: execution, inventory step
        # self.result_queue: all steps results
        self.parallel_queue = Queue()
        self.simple_queue = Queue()
        self.result_queue = Queue()
        self.retry_queue = Queue()
        self.watchdog_queue =Queue()

        if self.config.Triggers.post_deploy_active:
            queues = QueuesContainer()
            queues.add(self.parallel_queue)
            queues.add(self.simple_queue)
            queues.add(self.result_queue)
            queues.add(self.retry_queue)
            self.workers.append(WatchdogWorker(stop,
                                               self.watchdog_queue,
                                               queues,
                                               self.config.Triggers.post_deploy_script,
                                               self.config.Triggers.folder,
                                               )
                                )

        for n in range(0, self.config.Poller.result_workers):
            self.workers.append(ResultWorker(self.stop_workers, self.start_polling,
                                             self.result_queue, self.retry_queue,
                                             self.dlp_client))
        # only one worker for the execution/inventory step
        self.workers.append(StepWorker(self.stop_workers,
                                       self.simple_queue,
                                       self.result_queue,
                                       self.watchdog_queue
                                       )
                            )
        for n in range(0, self.config.Poller.parallel_workers):
            self.workers.append(StepWorker(self.stop_workers,
                                           self.parallel_queue,
                                           self.result_queue,
                                           self.watchdog_queue
                                           ))
        logger.info("Starting workers")
        for worker in self.workers:
            worker.start()

    def run(self):
        self.restore_state()
        # Wait before polling:
        # This is usefull when the agent is deployed in push mode, so it let the
        # push deployment finish before acting as a pull client
        #self.stop.wait(self.config.Poller.wait_poll)
        while not self.stop.is_set():
            if self.last_update_ts is None or (time.time() - self.last_update_ts) > 3 * 60:
                logger.info("Checking for agent updates **** ...")
                self.last_update_ts = time.time()
                base_path = os.path.dirname(os.path.abspath(__file__))

                if "library.zip" in base_path:
                    if base_path.endswith("\\") or  base_path.endswith("/"):
                        base_path = base_path[:-1]
                    base_path = os.path.dirname(base_path)

                try:
                    output, exitcode = launcher('triggers/update.sh', '', base_path)
                except Exception, e:
                    logger.error("Script error: %s" % e)
                logger.debug("Script output: %s" % output)

                if exitcode == 0:
                    logger.info("Update success.")
                elif exitcode == 42:
                    logger.info("Already on latest version.")
                else:
                    logger.info("Update error.")
            else:
                logger.info("Polling for new commands")
                for cmd_dict in self.dlp_client.get_commands():
                    if self.is_new_command(cmd_dict):
                        if self.pre_deploy_phase():
                            break
                        command = Command(cmd_dict, (self.parallel_queue, self.simple_queue), self.dlp_client)
                        self.commands.append(command)

            logger.info("Status:\n%s" % "\n".join(map(str, self.commands)))
            self.stop.wait(self.config.Poller.poll_interval)

        logger.info("Stopping workers")
        self.stop_workers.set()
        for worker in self.workers:
            worker.join()
        self.save_state()
        logger.info("Done")

    def save_state(self):
        if not self.result_queue.empty() or not self.retry_queue.empty():
            logger.info("Saving not sent results")
            results = []
            with open(self.state_path, 'w') as f:
                for queue in (self.retry_queue, self.result_queue):
                    while not queue.empty():
                        results.append(queue.get())
                        queue.task_done()
                pickle.dump(results, f)

    def restore_state(self):
        if os.path.exists(self.state_path):
            logger.info("Adding not sent results in queue")
            with open(self.state_path, 'r') as f:
                results = pickle.load(f)
            for result in results:
                self.result_queue.put(result)
            logger.debug("Added %d result(s) in queue" % len(results))
            self.start_polling.clear()
            os.unlink(self.state_path)
            # Wait to send all results
            # before getting new commands
            logger.info("Waiting for all results to be sent")
            while (not self.start_polling.is_set() and not self.stop.is_set()):
                self.stop.wait(5)

    def is_new_command(self, cmd_dict):
        for command in list(self.commands):
            # command has been rescheduled
            if command.id == cmd_dict['id'] and (command.is_failed or command.is_stopped):
                # removing old failed command
                logger.info("Removing old command %s" % command.id)
                self.commands.remove(command)
                return True
            if command.id == cmd_dict['id'] and command.is_running:
                logger.info("Command %s is already running, ignoring..." % cmd_dict['id'])
                return False
            if command.id == cmd_dict['id'] and command.is_done:
                logger.info("Command %s is already done, ignoring..." % cmd_dict['id'])
                return False
        return True

    def pre_deploy_phase(self):
        if not self.config.Triggers.pre_deploy_active:
            return False

        base_path = os.path.dirname(os.path.abspath(__file__))
        if "library.zip" in base_path:
            if base_path.endswith("\\") or  base_path.endswith("/"):
                base_path = base_path[:-1]
            base_path = os.path.dirname(base_path)
        path = "%s/%s" % (  self.config.Triggers.folder,
                            self.config.Triggers.pre_deploy_script)
        logger.info("Script path: %s" % path)
        try:
            output, exitcode = launcher(path, '', base_path)
        except Exception, e:
            logger.error("Script error: %s" % e)
        logger.debug("Script output: %s" % output)
        if exitcode == 0:

            logger.info("Machine unlocked, starting the post-deploy watchdog...")
            expires = time.time() + self.config.Triggers.post_deploy_timeout
            self.watchdog_queue.put(expires)
            return False
        else:
            logger.info("\033[32mUnlock process done, move-on aborted; waiting to next command call\033[0m")
            return True




if __name__ == "__main__":
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    h = logging.StreamHandler()
    h.setFormatter(formatter)
    h.setLevel(logging.DEBUG)
    logger.addHandler(h)
    logger.setLevel(logging.DEBUG)

    stop = Event()
    p = Poller(stop)
    p.start()
    try:
        while p.is_alive():
            p.join(500)
    except KeyboardInterrupt:
        print "Exiting."
        stop.set()
        p.join()
        print "Bye bye!"
