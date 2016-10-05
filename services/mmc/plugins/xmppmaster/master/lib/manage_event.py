#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os,platform
import os.path
import json
from multiprocessing import Process, Queue, TimeoutError
import threading
from utils import name_random, call_plugin
from  sleekxmpp import jid

class manage_event:
    def __init__(self, queue_in, objectxmpp):
        self.event=[]
        self.queue_in = queue_in
        self.namethread =  name_random(5, "threadevent")
        self.objectxmpp = objectxmpp
        print "****************************manage_event"
        self.threadevent = threading.Thread( name = self.namethread, target = self.manage_event_command)
        self.threadevent.start()

    def show_eventloop(self):
        print "boucle evenement"
        for i in self.event:
            print '------------\n%s\n------------'%i

    def addevent(self, event):
        self.event.append(event)

    def delevent(self, event):
        self.event.append(event)

    @staticmethod
    def create_TEVENT(to, action, sessionid, devent):
            return  {
                        'to' : to,
                        'action': action ,
                        'sessionid': sessionid,
                        'data' : {'Dtypequery' : 'TEVENT' ,'Devent' : devent },
                        'ret' : 0,
                        'base64' : False,
                        '_eventype' : 'TEVENT'
                    }

    def manage_event_loop(self):
        #traitement message interne
        for i in self.event:
            if not 'event' in i:
                # message de type loop
                jidto = jid.JID(str(i['to'])).bare
                msg={
                    'from' : jidto,
                    'to': jidto,
                    'body': {
                            'ret': i['ret'],
                            'sessionid':i['sessionid'],
                            'base64' : False
                            }
                    }
                if self.objectxmpp.session.isexist(i['sessionid']) and jidto == self.objectxmpp.boundjid.bare:
                    ##call plugin i['sessionid'] == msg['from'].bare
                    call_plugin( i['action'],
                                self.objectxmpp,
                                        i['action'],
                                        i['sessionid'],
                                        i['data'],
                                        msg,
                                        {}
                                        )

    def delmessage_loop(self, devent):
        #supprime message loop devent
        for i in self.event:
            if not 'event' in i:
                if i['data']['Devent'] == devent:
                    self.event.remove(i)
                    break;

    def delmessage_loop_Dtypequery(self, Dtypequery):
        #supprime message loop devent
        for i in self.event:
            if not 'event' in i:
                if i['data']['Dtypequery'] == Dtypequery:
                    self.event.remove(i)
                    break;

    def clear(self, sessionid):
        self.event = [x for x in self.event if x['sessionid'] != sessionid]

    def manage_event_command(self):
        try:
            while True:
                try:
                    #lit event
                    print "attente event"
                    event = self.queue_in.get(5)
                    print "MESSAGE QUEUE %s"%event
                    if event=="quit":
                        break
                    self.show_eventloop()
                    print "event recu *********************"%event
                    if 'sessionid' in event and '_eventype' in event:
                        if 'result' in event['data'] and \
                            'command' in event['data']['result'] and \
                            'codeerror' in event['data']['result'] and \
                            'Dtypequery'  in event['data']['result'] and \
                            'Devent'  in event['data']['result'] :
                            msg = { 
                                    'ret' : event['ret'],
                                    'sessionid' : event['sessionid'],
                                    'base64' : event['base64'],
                                    'action': event['action'],
                                    'data' : {
                                        'resultcommand'  :  event['data']['result']['resultcommand'],
                                        'command' :  event['data']['result']['command'],
                                        'codeerror' : event['data']['result']['codeerror'],
                                        'Dtypequery' : event['data']['Dtypequery'],
                                        'Devent': event['data']['Devent']
                                    }
                            }
                        else:
                            msg = { 
                                    'ret' : event['ret'],
                                    'sessionid' : event['sessionid'],
                                    'base64' : event['base64'],
                                    'action': event['action'],
                                    'data' : {
                                        'Dtypequery' : event['data']['Dtypequery'],
                                        'Devent': event['data']['Devent']
                                    }
                            }
                        print "SEND MESSAGE %s"%msg
                        self.objectxmpp.send_message( mto = event['to'],
                                            mbody=json.dumps(msg),
                                            mtype='chat')
                    else:
                        self.addevent(event)

                except TimeoutError:
                    print "TimeoutError"
 
        except KeyboardInterrupt:
            pass
        finally:
            print "manage_event end"
