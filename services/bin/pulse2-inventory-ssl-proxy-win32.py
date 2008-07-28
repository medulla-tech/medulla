
import win32serviceutil
import win32service
import win32event
import winerror
import pywintypes
import string
import os
import os.path
import sys
import twisted
import logging
import logging.config

from pulse2.proxyssl import initialize
from pulse2.proxyssl.config import Pulse2InventoryProxyConfig

class Pulse2ProxySsl(win32serviceutil.ServiceFramework):

    _svc_name_ = "Pulse2ProxySsl"
    _svc_display_name_ = "Pulse 2 Proxy SSL"

    def __init__(self,args):
        import servicemanager
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        curdir = os.path.dirname(__file__)
        if curdir.endswith("library.zip"):
            curdir = os.path.dirname(curdir)
        self.inifile = os.path.join(curdir, "p2ipc.ini")
        os.chdir(curdir)
        if not os.path.exists(self.inifile):
            print "File '%s' does not exist." % self.inifile
            sys.exit(3)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTING,(self._svc_display_name_, ''))

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def init(self):
        config = Pulse2InventoryProxyConfig()
        config.setup(self.inifile)
        logging.config.fileConfig(self.inifile)
        logger = logging.getLogger()
        initialize(config)

    def SvcDoRun(self):
        import servicemanager
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED,(self._svc_display_name_, ''))
        self.CheckForQuit()
        self.init()
        twisted.internet.reactor.run(installSignalHandlers=0)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STOPPED,(self._svc_display_name_, ''))

    def CheckForQuit(self):
        retval = win32event.WaitForSingleObject(self.hWaitStop, 10)
        if not retval == win32event.WAIT_TIMEOUT:
            # Received Quit from Win32
            twisted.internet.reactor.stop()
        twisted.internet.reactor.callLater(1.0, self.CheckForQuit)

if __name__=='__main__':
    win32serviceutil.HandleCommandLine(Pulse2ProxySsl)


