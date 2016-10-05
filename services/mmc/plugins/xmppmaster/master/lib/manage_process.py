#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os,platform
import os.path
import json
from multiprocessing import Process, Queue, TimeoutError
import threading
from utils import simplecommandestr

import subprocess
from threading import Timer
import logging


##!/usr/bin/env python
## -*- coding: utf-8 -*-

#import sys,os,platform
#import os.path
#import json
#from multiprocessing import Process, Queue, TimeoutError
#import threading
#from lib.utils import simplecommandestr
#import traceback

import subprocess
from threading import Timer
logger = logging.getLogger()

class mannageprocess:

    def __init__(self, queue_out_session) :
        self.processtable = []
        self.queue_out_session = queue_out_session
        logging.info('manage process start')


    def add_processcommand(self, command , sessionid, eventstart = False, eventfinish = False, eventerror = False, timeout = 50, keysdescriptor = []):
        createprocesscommand = Process(target=self.processcommand, args=(command ,
                                                                         self.queue_out_session,
                                                                         sessionid,
                                                                         eventstart,
                                                                         eventfinish ,
                                                                         eventerror ,
                                                                         timeout ,
                                                                         keysdescriptor))
        self.processtable.append(createprocesscommand)
        createprocesscommand.start()

    def processcommand( self,  command , queue_out_session, sessionid, eventstart, eventfinish, eventerror, timeout, keysdescriptor):
        #il y a 2 types de messages event ceux de la boucle interne et ceux envoyé en TEVENT
        try:
            #structure message for msgout
            msgout = {
                        'event': "",
                        'sessionid': sessionid,
                        'result' : { 'codeerror' : 0, 'resultcommand' : '','command' : command },
            }
            if eventstart != False:
                #ecrit dans queue_out_session l'evenement eventstart
                if '_eventype' in eventstart and '_eventype' == 'TEVENT':
                    msgout['event'] = eventstart
                    queue_out_session.put(msgout)
                else:
                    queue_out_session.put(eventstart)
            cmd = cmdx(command,timeout)
            if cmd.code_error == 0 and eventfinish != False:
                ev = eventfinish
            elif cmd.code_error != 0 and eventfinish != False:
                ev = eventerror
            else:
                ev = False

            print "================================================"
            print " execution commande in process"
            print "================================================"
            print cmd.code_error
            print cmd.stdout
            print "================================================"

            if ev != False:
                if '_eventype' in ev and '_eventype' == 'TEVENT':
                    #ecrit dans queue_out_session le TEVENT
                    msgout['event'] = ev
                    #msgout['result']['resultcommand'] = cmd['result']
                    msgout['result']['resultcommand'] = cmd.stdout
                    msgout['result']['codeerror'] = cmd.code_error
                    queue_out_session.put(msgout)
                else:
                    ev['data']['result'] = {'codeerror': cmd.code_error,'command' : command  }
                    for t in keysdescriptor:
                        if t == 'codeerror' or t=='command': 
                            pass
                        elif t == '@resultcommand' :
                            ev['data']['result']['@resultcommand'] = cmd.stdout
                        elif  t.endswith('lastlines'):
                            nb = t.split("@")
                            nb1 = -int(nb[0])
                            tab = [x for x in cmd.stdout.split(os.linesep) if x !='']
                            tab = tab[nb1:]
                            ev['data']['result'][t] = os.linesep.join(tab)
                        elif t.endswith('firstlines'):
                            nb = t.split("@")
                            nb1 = int(nb[0])
                            tab = [x for x in cmd.stdout.split(os.linesep) if x !='']
                            tab = tab[:nb1]
                            ev['data']['result'][t] = os.linesep.join(tab)
                    queue_out_session.put(ev)

        except TimeoutError:
            logging.error("TimeoutError process  %s sessionid : %s"%(command,sessionid))
        except KeyboardInterrupt:
            logging.warn("KeyboardInterrupt process  %s sessionid : %s"%(command,sessionid))
            sys.exit(0)
        except :
            traceback.print_exc(file=sys.stdout)
            logging.error("error execution process %s sessionid : %s"%(command,sessionid))
            sys.exit(0)




class cmdx(object):
    def __init__(self, cmd, timeout):
        self.cmd=cmd
        self.timeout = timeout
        self.timeoutbool = False
        self.code_error = 0
        self.run()

    def kill_proc(self, proc):
        self.timeoutbool = True;
        proc.kill()

    def run(self):
        self.proc = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #kill_proc = lambda p: p.kill()
        timer = Timer(self.timeout, self.kill_proc, [self.proc])
        try:
            timer.start()
            stdout,stderr = self.proc.communicate()
        finally:
            timer.cancel()
        #self.stderr = stderr
        self.stdout = stdout

        self.code_error = self.proc.returncode
        if self.timeoutbool:
            self.stdout = "error : timeout %s"%self.timeout
            #self.code_error = 150
