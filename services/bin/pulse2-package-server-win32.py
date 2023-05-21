# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import win32serviceutil
import win32service
import win32event
import winerror  # pyflakes.ignore
import pywintypes  # pyflakes.ignore
import os
import os.path
import sys

import twisted
import twisted.copyright
import logging
import logging.config


class Pulse2PackageServer(win32serviceutil.ServiceFramework):
    _svc_name_ = "Pulse2PackageServer"
    _svc_display_name_ = "Pulse 2 Package Server"

    def __init__(self, args):
        import servicemanager

        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        curdir = os.path.dirname(__file__)
        if curdir.endswith("library.zip"):
            curdir = os.path.dirname(curdir)
        self.inifile = os.path.join(curdir, "package-server.ini")
        os.chdir(curdir)
        if not os.path.exists(self.inifile):
            print(f"File '{self.inifile}' does not exist.")
            sys.exit(3)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTING,
            (
                self._svc_display_name_,
                f" Using configuration file: {self.inifile}",
            ),
        )

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def init(self, config):
        from pulse2.package_server import (
            ThreadLauncher,
            init_logger_debug,
            getRevision,
            getVersion,
        )

        logging.config.fileConfig(self.inifile)
        logger = logging.getLogger()
        init_logger_debug()
        logger.info(f"Pulse 2 Package Server {getVersion()} starting...")
        logger.info(f"Pulse 2 Package Server build '{str(getRevision())}'")
        logger.info("Using Python %s" % sys.version.split("\n")[0])
        logger.info(f"Using Python Twisted {twisted.copyright.version}")
        if config.use_iocp_reactor:
            logger.info("Using IOCP reactor")
        ThreadLauncher().initialize(config)

    def SvcDoRun(self):
        import servicemanager

        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_display_name_, ""),
        )
        from pulse2.package_server.config import P2PServerCP

        config = P2PServerCP()
        config.setup(self.inifile)
        if config.use_iocp_reactor:
            from twisted.internet import iocpreactor

            iocpreactor.install()
        self.CheckForQuit()
        self.init(config)
        twisted.internet.reactor.run(installSignalHandlers=0)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_display_name_, ""),
        )

    def CheckForQuit(self):
        retval = win32event.WaitForSingleObject(self.hWaitStop, 10)
        if retval != win32event.WAIT_TIMEOUT:
            # Received Quit from Win32
            twisted.internet.reactor.stop()
        twisted.internet.reactor.callLater(1.0, self.CheckForQuit)


if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(Pulse2PackageServer)
