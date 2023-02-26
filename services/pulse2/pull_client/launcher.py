# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
import os
import time
from base64 import b64encode
from threading import Thread, Event
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
import Queue
import logging

from utils import get_launcher_env


logger = logging.getLogger(__name__)


class ReadFlux(Thread):
    def __init__(self, pipe, output_queue, prepend=None):
        Thread.__init__(self)
        self.pipe = pipe
        self.output_queue = output_queue
        self.prepend = prepend
        self._stop = Event()

    def run(self):
        while not self._stop.is_set():
            line = self.pipe.readline() # blocking
            if not line:
                break
            self.output_queue.put("%f %s %s" % (time.time(),
                                                self.prepend,
                                                b64encode(line)
                                                )
                                  )

    def stop(self):
        self._stop.set()


def launcher(start_file, params, workdir):
    """
    Function for running commands in cygwin
    """
    output_queue = Queue.Queue()
    output = ""
    stf = NamedTemporaryFile(mode="w", delete=False)
    cmd_bash = "%s %s" % (start_file, params)
    stf.write(cmd_bash)
    stf.close()

    output_queue.put("%f C: %s\n" % (time.time(), cmd_bash))
    logger.debug("Running %s" % cmd_bash)
    p = Popen(["bash", stf.name],
              bufsize=0,
              stderr=PIPE,
              stdout=PIPE,
              env=get_launcher_env(),
              cwd=workdir)

    err_reader = ReadFlux(p.stderr, output_queue, prepend="E:")
    err_reader.daemon = True
    err_reader.start()
    std_reader = ReadFlux(p.stdout, output_queue, prepend="O:")
    std_reader.daemon = True
    std_reader.start()
    # Wait for command to end
    exitcode = p.wait()
    logger.debug("Finished %s, exitcode: %d" % (cmd_bash, exitcode))
    output_queue.put("%f X: %d\n" % (time.time(), exitcode))
    err_reader.stop()
    std_reader.stop()
    # get and return the output
    while not output_queue.empty():
        output += output_queue.get()
        output_queue.task_done()

    os.unlink(stf.name)

    return output, exitcode
