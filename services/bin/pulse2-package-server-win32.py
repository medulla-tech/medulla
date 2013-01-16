#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import win32serviceutil
import win32service
import win32event
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

    def __init__(self,args):
        import servicemanager
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        curdir = os.path.dirname(__file__)
        if curdir.endswith("library.zip"):
            curdir = os.path.dirname(curdir)
        self.inifile = os.path.join(curdir, "package-server.ini")
        os.chdir(curdir)
        if not os.path.exists(self.inifile):
            print "File '%s' does not exist." % self.inifile
            sys.exit(3)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTING,(self._svc_display_name_, ' Using configuration file: %s' % self.inifile))

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def init(self, config):
        from pulse2.package_server import ThreadLauncher, init_logger_debug, getRevision, getVersion
        logging.config.fileConfig(self.inifile)
        logger = logging.getLogger()
        init_logger_debug()
        logger.info("Pulse 2 Package Server %s starting..." % getVersion())
        logger.info("Pulse 2 Package Server build '%s'" % str(getRevision()))
        logger.info("Using Python %s" % sys.version.split("\n")[0])
        logger.info("Using Python Twisted %s" % twisted.copyright.version)
        if config.use_iocp_reactor:
            logger.info("Using IOCP reactor")
        ThreadLauncher().initialize(config)

    def SvcDoRun(self):
        import servicemanager
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED,(self._svc_display_name_, ''))
        from pulse2.package_server.config import P2PServerCP
        config = P2PServerCP()
        config.setup(self.inifile)
        if config.use_iocp_reactor:
            from twisted.internet import iocpreactor
            iocpreactor.install()
        self.CheckForQuit()
        self.init(config)
        twisted.internet.reactor.run(installSignalHandlers=0)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STOPPED,(self._svc_display_name_, ''))

    def CheckForQuit(self):
        retval = win32event.WaitForSingleObject(self.hWaitStop, 10)
        if not retval == win32event.WAIT_TIMEOUT:
            # Received Quit from Win32
            twisted.internet.reactor.stop()
        twisted.internet.reactor.callLater(1.0, self.CheckForQuit)

if __name__=='__main__':
    win32serviceutil.HandleCommandLine(Pulse2PackageServer)

