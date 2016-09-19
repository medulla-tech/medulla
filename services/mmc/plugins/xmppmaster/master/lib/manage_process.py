#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os,platform
import os.path
import json
from multiprocessing import Process, Queue, TimeoutError
import threading
from utils import simplecommandestr

class mannageprocess:

    def __init__(self, queue_out_session) :
        self.processtable = []
        self.queue_out_session = queue_out_session

    def add_processcommand(self, cmddata , sessionid, eventstart = False, eventfinish = False, eventerror = False):
        createprocesscommand = Process(target=self.processcommand, args=(cmddata , self.queue_out_session, sessionid, eventstart, eventfinish , eventerror ))
        self.processtable.append(createprocesscommand)
        createprocesscommand.start()

    def processcommand( self,  cmddata , queue_out_session, sessionid, eventstart, eventfinish, eventerror):
        #il y a 2 type de messages event ceux de la boucle interne et ceux envoyé en TEVENT
        try: 
            #structure message for msgout
            msgout = {
                        'event': "",
                        'sessionid': sessionid,
                        'result' : { 'codeerror' : 0, 'resultcommand' : '','cmddata' : cmddata },
            }
            if eventstart != False:
                #ecrit dans queue_out_session l'evenement eventstart
                if '_eventype' in eventstart and '_eventype' == 'TEVENT':
                    msgout['event'] = eventstart
                    queue_out_session.put(msgout)
                else:
                    queue_out_session.put(eventstart)

            cmd = simplecommandestr(cmddata)

            if cmd['code'] == 0 and eventfinish != False:
                ev = eventfinish
            elif cmd['code'] != 0 and eventfinish != False:
                ev = eventerror
            else:
                ev = False

            if ev != False:
                if '_eventype' in ev and '_eventype' == 'TEVENT':
                    #ecrit dans queue_out_session le TEVENT
                    msgout['event'] = ev
                    msgout['result']['resultcommand'] = cmd['result']
                    msgout['result']['codeerror'] = cmd['code']
                    queue_out_session.put(msgout)
                else:
                    ev['data']['result'] = {'codeerror': cmd['code'],'resultcommand' : cmd['result'],'cmddata' : cmddata  }
                    queue_out_session.put(ev)

        except TimeoutError:
            pass
        except KeyboardInterrupt:
            sys.exit(0)

