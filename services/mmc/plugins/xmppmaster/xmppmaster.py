import threading
import time
import logging

from mmc.plugins.xmppmaster.config import xmppMasterConfig
from mmc.plugins.xmppmaster.master.agentmasterjson2 import doTask, stopxmpp
logger = logging.getLogger()

class xmppMasterthread(threading.Thread): 
    def __init__(self, args=(), kwargs=None):
        threading.Thread.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.disable = xmppMasterConfig().disable
        return
    
    def run(self):
        doTask()
        #i = 0
        #while i < 20:
            #dede.affiche()
            #logger.info("xmmpMasterthread %s %s %s"
                        #% (self.args,xmppMasterConfig().Server,xmppMasterConfig().Port ))
            #time.sleep(5)
            #i += 1
    def stop(self):
        stopxmpp()