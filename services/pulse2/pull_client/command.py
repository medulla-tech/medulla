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
import logging
import time
from datetime import datetime
import Queue
import shutil
import traceback
from StringIO import StringIO
import subprocess

from launcher import launcher
from utils import get_packages_dir, get_launcher_env


logger = logging.getLogger(__name__)


class CommandFailed(Exception):
    pass


class StepCantRun(Exception):
    pass


class Command(object):

    def __init__(self, command, queues, dlp_client):
        self.dlp_client = dlp_client
        self.command = command
        self.created = time.time()
        self.parallel_queue, self.simple_queue = queues
        self.to_do = Queue.Queue()
        self.steps = []
        self.done = False
        self.failures = 0
        self.interval = (self.end_date - self.start_date) / float(self.max_failures)
        self.interval = 5
        logger.debug("Command fail interval is %s" % self.interval)
        logger.debug("Max failures is: %i" % self.max_failures)
        # get only steps that haven't been done in a previous run
        # because of agent restart for example
        for step_name in self.command['todo']:
            if not step_name == Steps.DONE.name:
                step = getattr(Steps, step_name.upper()).klass(self, step_name)
                self.to_do.put(step)
        # Put first step in the work queue
        self.next_step()

    @property
    def id(self):
        return self.command['id']

    @property
    def start_date(self):
        return self.command['start_date']

    @property
    def end_date(self):
        return self.command['end_date']

    @property
    def max_failures(self):
        return self.command['max_failures']

    @property
    def package_uuid(self):
        return self.command['package_uuid']

    @property
    def start_file(self):
        return self.command['start_file']

    @property
    def params(self):
        return self.command['params']

    def next_step(self):
        try:
            step = self.to_do.get(False)
        except Queue.Empty:
            self.done = True
            logger.info("%s finished." % self)
        else:
            if step.name in (Steps.EXECUTE.name, Steps.INVENTORY.name):
                logger.debug("Add %s in simple_qeue" % step)
                self.simple_queue.put(step)
            else:
                logger.debug("Add %s in parallel_queue" % step)
                self.parallel_queue.put(step)
            self.to_do.task_done()

    def failed_step(self):
        self.failures += 1

    @property
    def is_failed(self):
        return self.failures >= self.max_failures

    @property
    def is_done(self):
        return self.done

    @property
    def is_running(self):
        return not (self.is_failed or self.is_done)

    def __repr__(self):
        d = datetime.now() - datetime.fromtimestamp(self.created)
        d = d.total_seconds()
        return "<Command(%s, to_do=%s, failures=%s, created=%is ago running=%s)>" % (self.id,
                                                                                     self.to_do.qsize(),
                                                                                     self.failures,
                                                                                     d, self.is_running)


class Result(object):

    def __init__(self, step_name, command_id, stdout, stderr, exitcode):
        self.command_id = command_id
        self.step_name = step_name
        self.stdout = stdout
        self.stderr = stderr
        self.exitcode = exitcode

    @property
    def is_success(self):
        return self.exitcode == 0

    def __repr__(self):
        return "<Result(%s, step=%s, cmd=%s)" % (self.exitcode, self.step_name, self.command_id)


class Step(object):
    prio = 0

    def __init__(self, command, name):
        self.command = command
        self.name = name
        self.next_run = time.time()

    def can_run(self):
        if self.command.failures >= self.command.max_failures:
            logger.error("%s max failed." % self.command)
            raise CommandFailed()
        if self.next_run > time.time():
            logger.debug("%s waiting next run." % self)
            raise StepCantRun()
        return True

    def start(self):
        logger.debug("%s running" % self)
        try:
            stdout, exitcode = self.run()
        except:
            # If a step makes a traceback
            # send it back as a failed result
            out = StringIO()
            traceback.print_exc(file=out)
            stdout = "%f E: %s" % (time.time(), out.getvalue())
            out.close()
            exitcode = 1
            logger.exception("Error in %s" % self)
        result = Result(self.name, self.command.id, stdout, "", exitcode)
        if not result.is_success:
            self.command.failed_step()
            self.next_run = time.time() + self.command.interval
        return result

    def run(self):
        raise NotImplementedError("Must be implemented in suclass")

    def __repr__(self):
        return "<Step(%s, next_run=%s, cmd=%s)>" % (self.name, self.next_run, self.command.id)


class NoopStep(Step):

    def run(self):
        return ("%f O: Ignored in pull mode." % time.time(), 0)


class WolStep(Step):

    def run(self):
        return ("%f O: I'm awake!" % time.time(), 0)


class UploadStep(Step):

    def run(self):
        path = self.command.dlp_client.get_package(self.command.package_uuid,
                                                   workdir=get_packages_dir())
        if path:
            return ("%f O: Package downloaded at %s" % (time.time(), path), 0)
        else:
            return ("%f E: Failed to download package" % time.time(), 1)


class ExecuteStep(Step):

    def run(self):
        package_dir = os.path.join(get_packages_dir(), self.command.package_uuid)
        output, exitcode = launcher(self.command.start_file, self.command.params, package_dir)
        return (output, exitcode)


class DeleteStep(Step):

    def run(self):
        package_dir = os.path.join(get_packages_dir(), self.command.package_uuid)
        shutil.rmtree(package_dir)
        os.unlink(package_dir + ".zip")
        return ("%f O: Package files removed" % time.time(), 0)


class InventoryStep(Step):

    def run(self):
        p = subprocess.Popen(['perl', 'fusioninventory-agent', '--stdout'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=get_launcher_env(),
                             cwd=get_launcher_env()['FUSION_BIN_PATH'])
        inventory, error = p.communicate()
        if not p.returncode == 0:
            return ("%f E: %s" % (time.time(), error), p.returncode)
        # Send the inventory to the DLP
        if self.command.dlp_client.send_inventory(inventory):
            return ("%f O: Inventory sent to the Pulse Inventory Server" % time.time(), 0)
        return ("%f E: Failed to send inventory to the Pulse Inventory Server" % time.time(), 1)


class Steps:
    WOL = type('Step', (object,), {'name': 'wol', 'klass': WolStep})
    UPLOAD = type('Step', (object,), {'name': 'upload', 'klass': UploadStep})
    EXECUTE = type('Step', (object,), {'name': 'execute', 'klass': ExecuteStep})
    DELETE = type('Step', (object,), {'name': 'delete', 'klass': DeleteStep})
    INVENTORY = type('Step', (object,), {'name': 'inventory', 'klass': InventoryStep})
    REBOOT = type('Step', (object,), {'name': 'reboot', 'klass': NoopStep})
    HALT = type('Step', (object,), {'name': 'halt', 'klass': NoopStep})
    DONE = type('Step', (object,), {'name': 'done'})
