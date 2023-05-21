#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later


import logging

logging.basicConfig()

import queue
import threading
import tempfile
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from unittest import TestCase, main

from pulse2agent.types import CC
from pulse2agent.vpn import VPNLaunchControl


class ProcessSimulator(object):
    output = [
        ("establishing the connection", ""),
        ("", "probe failed"),
        ("next", ""),
        ("another", ""),
        ("", "unable reach the host"),
        ("end", ""),
    ]

    timeout = 0.5
    body = """
#!/usr/bin/python
import sys
import time

for (out, err) in %s:
    if out is not None:
        sys.stdout.write(out)
    if err is not None:
        sys.stderr.write(err)
    time.sleep(%d)
    """ % (
        output,
        timeout,
    )

    t_file = None

    def __init__(self):
        self.t_file = tempfile.NamedTemporaryFile()
        with open(self.t_file.name, "w") as f:
            f.write(self.body)

    def __enter__(self):
        return self.t_file

    def __exit__(self, type, value, traceback):
        self.t_file.close()


class ProcessSucceed(ProcessSimulator):
    body = """#!/bin/bash\nexit 0;"""


class ProcessFailed(ProcessSimulator):
    body = """#!/bin/bash\nexit 1;"""


class ConfigHelper(object):
    class vpn:
        host = "localhost"
        port = 5555
        command = ""
        command_args = ""


class Test00_VPNLaunchControl(TestCase):
    def setUp(self):
        pass

    def test00_launch_and_catch_the_output(self):
        """
        - create a simple script with active stdout and stderr
        - launch it and catch its output
        """
        queue = queue.Queue()

        with ProcessSimulator() as script:
            config = ConfigHelper()
            config.vpn.command = "python"
            config.vpn.command_args = script.name

            launch_vpn = VPNLaunchControl(config, queue)

            def pb():
                return True

            setattr(launch_vpn, "probe", pb)
            launch_vpn.start()

            outs = errs = ""
            for out, err in ProcessSimulator.output:
                outs += out
                errs += err

            p_outs, p_errs = queue.get()

            self.assertEqual(outs, p_outs)
            self.assertEqual(errs, p_errs)

    def test01_return_code_succeed(self):
        """Launched script returns 0"""

        queue = queue.Queue()

        with ProcessSucceed() as script:
            config = ConfigHelper()
            config.vpn.command = "sh"
            config.vpn.command_args = script.name

            launch_vpn = VPNLaunchControl(config, queue)

            def pb():
                return True

            setattr(launch_vpn, "probe", pb)
            ret = launch_vpn.start()

            self.assertEqual(ret, CC.VPN | CC.DONE)

    def test02_return_code_failed(self):
        """Launched script returns 1"""

        queue = queue.Queue()

        with ProcessFailed() as script:
            config = ConfigHelper()
            config.vpn.command = "sh"
            config.vpn.command_args = script.name

            launch_vpn = VPNLaunchControl(config, queue)

            def pb():
                return True

            setattr(launch_vpn, "probe", pb)
            ret = launch_vpn.start()

            self.assertEqual(ret, CC.VPN | CC.FAILED)

    def test03_probe_failed(self):
        """Unreachable server"""
        config = ConfigHelper()
        queue = queue.Queue()

        launch_vpn = VPNLaunchControl(config, queue)

        ret = launch_vpn.start()

        self.assertEqual(ret, CC.VPN | CC.REFUSED)

    def test04_probe_succeed(self):
        """Launched script returns 0"""

        def build_vpn_server(config):
            server = socket(AF_INET, SOCK_STREAM)
            server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            server.bind((config.vpn.host, config.vpn.port))
            server.listen(1)

            client_connection, address = server.accept()
            if client_connection:
                result = client_connection.recv(1024)  # pyflakes.ignore
                client_connection.close()

        with ProcessSucceed() as script:
            config = ConfigHelper()
            config.vpn.command = "sh"
            config.vpn.command_args = script.name

            t = threading.Thread(target=build_vpn_server, args=(config,))
            t.start()

            queue = queue.Queue()

            launch_vpn = VPNLaunchControl(config, queue)
            ret = launch_vpn.start()

            self.assertEqual(ret, CC.VPN | CC.DONE)


if __name__ == "__main__":
    if TestCase.__module__ != "twisted.trial.unittest":
        main()
