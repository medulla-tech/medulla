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

import os
import stat

from subprocess import Popen

import logging

from twisted.trial.unittest import TestCase


from mmc.plugins.support.process import PIDControl

PID_PATH = "/var/run/pulse2_ssh_support_test.pid"

logging.basicConfig()


class Daemonize(object):
    """Controls a little shell script executed as daemon."""

    filename = "./test_script.sh"

    args = ["setsid",
            filename,
            ">",
            "/dev/null",
            "2>&1",
            "&",
            "/dev/null",
            ]

    content = """#!/bin/sh
while true
do
    echo  "I'm a test daemon..."
    sleep 1
done
    """

    def create_script(self):
        """ Creates a simple script which will be daemonized"""
        if os.path.exists(self.filename):
            return
        with open(self.filename, "w") as f:
            f.write(self.content)
        os.chmod(self.filename, stat.S_IEXEC)

    def execute(self):
        """ Opens a subprocess and executes them as daemon """
        f_null = open(os.devnull, "w")

        p = Popen(self.args,
                  stdout=f_null,
                  stderr=f_null
                  )
        return p


    def remove_script(self):
        """Removes the test script """
        if os.path.exists(self.filename):
            os.unlink(self.filename)


class Config(object):
    session_timeout = 10
    url = "root@127.0.0.1"
    identify_file = "/dev/null"
    pid_path = PID_PATH
    check_pid_delay = 2



class Test01_PIDControl(TestCase):

    def setUp(self):
        self.daemon = Daemonize()
        self.daemon.create_script()


    def test01_no_probe(self):
        """ Process not detected yet """
        pid_control = PIDControl(PID_PATH)
        self.assertFalse(pid_control.probe())


    def test02_set_pid_false(self):
        """ Process not executed yet """

        pid_control = PIDControl(PID_PATH)

        args = ["/bin/sh"] + self.daemon.args[1:]

        ret = pid_control.set_daemon_pid(args)
        logging.getLogger().info("ret: %s" % ret)
        self.assertFalse(ret)


    def test03_set_pid(self):
        """ Creating the PID file """

        pid_control = PIDControl(PID_PATH)
        self.daemon.execute()

        args = ["/bin/sh"] + self.daemon.args[1:]

        ret = pid_control.set_daemon_pid(args)
        logging.getLogger().info("ret: %s" % ret)
        self.assertTrue(ret)

    def test04_probe(self):
        """ Process will be detected """
        pid_control = PIDControl(PID_PATH)
        self.assertTrue(pid_control.probe())

    def test05_established(self):
        """ Process will be detected """
        pid_control = PIDControl(PID_PATH)
        self.assertTrue(pid_control.established)

    def test06_kill(self):
        """ Killing the process """
        pid_control = PIDControl(PID_PATH)
        pid_control.kill()

        ret = pid_control.established or pid_control.probe()
        self.assertFalse(ret)

    def tearDown(self):
        self.daemon.remove_script()



