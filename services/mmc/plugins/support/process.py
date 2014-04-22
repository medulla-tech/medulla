# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2014 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

""" Common utils for the process control. """

import os
import time
import logging

from random import randrange
import psutil

from twisted.internet import reactor
from twisted.internet.protocol import ProcessProtocol
from twisted.internet.defer import succeed, inlineCallbacks
from twisted.internet.task import deferLater
from twisted.internet.error import ProcessDone


class ForkingProtocol(ProcessProtocol):
    """ Protocol to fork a SSH session """

    def __init__(self, callback):
        ProcessProtocol()
        self.logger = logging.getLogger()

        self.callback = callback


    def connectionMade(self):
        self.logger.debug("SSH Tunnel: Opening of daemon started")


    def outReceived(self, data):
        self.logger.debug("SSH Tunnel: process data received: %s" % (data))
        ProcessProtocol.outReceived(self, data)

    def errReceived(self, reason):
        self.logger.warn("SSH Tunnel: process failed: %s" % (reason))
        self.transport.loseConnection()
        ProcessProtocol.errReceived(self, reason)

    def processEnded(self, reason):
        err = reason.trap(ProcessDone)
        if err==ProcessDone:
            self.logger.debug("SSH Tunnel: process successfully ended")
        else:
            self.logger.warn("SSH Tunnel: closing failed: %s" % (reason))

        self.callback(reason)



class PIDControl(object):
    """
    Several operations over given process.

    Includes some checks of existing process, PID file reference control,
    and a classic killing of process.
    """

    daemon_proc = None
    pid_path = "/var/run/pulse2/ssh_support"

    def __init__(self, pid_path):
        """
        @param pid_path: path of PID file
        @type pid_path: str
        """
        self.pid_path = pid_path
        self.logger = logging.getLogger()

        if self.established:
            if self.probe():
                self.logger.info("SSH Tunnel: Found tunnel pid=%d" % self.daemon_proc.pid)


    def set_daemon_pid(self, args):
        """
        Checks the process and creates its PID file.

        @param args: command
        @type args: list

        @return: True if process found
        @rtype: bool
        """

        for p in psutil.process_iter():
            if p.cmdline == args :
                self.daemon_proc = p
                self.logger.info("SSH Tunnel: pid=%d" % p.pid)
                self.write_pid_file()
                return True
        self.logger.warn("SSH Tunnel: Can't find the pid for: %s" % " ".join(args))
        return False


    def kill(self):
        """ Kills the process. """
        self.logger.info("SSH Tunnel: closing the ssh tunel")
        try:
            self.daemon_proc.kill()
        except Exception, e:
            self.logger.warn("SSH Tunnel: close failed: %s" % str(e))

        self.remove_pid_file()


    def probe(self):
        """
        Looks for existing process and creates a common Process instance.

        @return: True if process already exists
        @rtype: bool
        """
        pid = self.get_pid_from_file()
        if pid:
            self.daemon_proc = psutil.Process(pid)
            return True
        else:
            return False

    def get_pid_date(self):
        """
        Gets the execution time of process.

        @return: timestamp of execution
        @rtype: float
        """
        if self.established:
            return self.daemon_proc.create_time

    def get_pid_from_file(self):
        """
        Gets the PID of process from PID file.

        @return: PID or None if not exists
        @rtype: int
        """

        if not os.path.exists(self.pid_path):
            return None

        with open(self.pid_path, "r") as f:
            lines = f.readlines()
            if len(lines) > 0:
                try:
                    pid = int(lines[0].strip())
                    return pid
                except ValueError:
                    self.logger.warn("SSH Tunnel: Unable to get pid from %s" % self.pid_path)


    def write_pid_file(self):
        """ Writes the PID into PID file."""
        with open(self.pid_path, "w") as f:
            line = "%s\n" % str(self.daemon_proc.pid)
            f.write(line)

    @property
    def established(self):
        """ Returns True if the process already opened """
        return os.path.exists(self.pid_path)


    def remove_pid_file(self):
        """ Removes the PID file """
        if self.established:
            os.unlink(self.pid_path)



class TunnelBuilder(object):

    """
    Provides the forking of given process.

    Spawns a process and controls its life-time.
    Instance of this class must be referenced as singleton
    to avoid the duplicities of controlled process.
    """

    pid_control = None
    port = 0
    config = None

    def __init__(self, config):
        """
        Initialize the builder.

        The builder checks immediatelly a occurence of PID file and process;
        When a process is already established, creates a expirator
        which provides a responding life-time.
        If the difference between start time of checked process
        and current time is greater than timeout, this process
        will be considered as already expired.

        @param config: support config instance
        @type config: PluginConfig
        """
        self.config = config
        self.pid_control = PIDControl(config.pid_path)
        self.logger = logging.getLogger()

        if self.established:
            pid_date = self.pid_control.get_pid_date()
            delay = pid_date + self.config.session_timeout - time.time()
            if delay > 0:
                self.logger.info("SSH Tunnel: Already established - session will be expired at: %d seconds" % int(delay))
            else:
                delay = 1
                # !!! do not put delay = 0 !!!
                self.logger.info("SSH Tunnel: Found tunnel expired")

            self._do_expire(delay)



    @property
    def args(self):
        """
        List of arguments to open a deamon of ssh session.

        @return: ssh command
        @rtype: list
        """
        return [self.config.ssh_path,
                # this options provides the daemonizing of SSH session
                # so no need nohup execution or other utils ...
                "-f", "-N",
                self.config.url,
                "-R%d:127.0.0.1:22" % self.port,
                "-o",
                "IdentityFile=%s" % self.config.identify_file,
                "-o",
                " CheckHostIP=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-o",
                "PasswordAuthentication=no",
                "-o",
                "StrictHostKeyChecking=no",
                ]


    def open(self):
        """
        Creates a daemon ssh session.

        @return: True if a new session opened
        @rtype: Deferred
        """
        # port choice placed here to generate a random
        # number of port for each new process open
        self.port = randrange(2200, 2299)

        if not self.pid_control.probe():
            self.logger.info("SSH Tunnel: establishing...")
            return self._open()
        else:
            self.logger.warn("process already opened! (pid=%d)" % self.pid_control.daemon_proc.pid)
            return succeed(False)


    @inlineCallbacks
    def _open(self):
        """
        Creates a daemon ssh session.

        @return: True if a new session opened
        @rtype: Deferred
        """
        protocol = ForkingProtocol(TunnelBuilder.process_ended)
        reactor.spawnProcess(protocol,
                             self.args[0],
                             self.args,
                             usePTY=True)
        try:
            yield deferLater(reactor,
                       self.config.check_pid_delay,
                       self.pid_control.set_daemon_pid,
                       self.args)
            yield self._do_expire()

        except Exception, e:
            self.logger.warn("SSH Tunnel: PID check failed: %s" % e)


    def _do_expire(self, delay=None):
        """
        Controls the expiration of launched process.

        @param delay: session duration
        @type delay: int
        """

        timeout_d = deferLater(reactor,
                               delay or self.config.session_timeout,
                               self.pid_control.kill)
        @timeout_d.addCallback
        def cb_timeout(reason):
            self.logger.info("SSH Tunnel: timeout reached, session closed")

        @timeout_d.addErrback
        def eb_timeout(failure):
            self.logger.warn("SSH Tunnel: timeout closing failed: %s" % failure)

        return True




    def close(self):
        """ Kills the process """
        return self.pid_control.kill()

    @property
    def established(self):
        """ Returns True if the process already opened """
        return self.pid_control.established

    @staticmethod
    def process_ended(reason):
        pass




