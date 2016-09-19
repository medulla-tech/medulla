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
                    print '********APPELLE PLUGIN ****************'
                    call_plugin( i['action'],
                                self.objectxmpp,
                                        i['action'],
                                        i['sessionid'],
                                        i['data'],
                                        msg,
                                        {}
                                        )
                    #print '******************************'

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

    #def manage_event_command(self):
        #try:
            #while True:
                #try:
                    ##lit event
                    #print "attente event"
                    #event = self.queue_in.get(5)
                    #print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                    #print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                    #print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                    #print 
                    #if event=="quit":
                        #break
                    #self.show_eventloop()
                    #print "event recu *********************"%event
                    #if 'sessionid' in event and 'event' in event:
                        #for i in self.event:
                            #if i['sessionid'] == event['sessionid'] and event['event'] == i['data']['Devent']:
                                #i['ret'] = event['result']['codeerror']
                                #i['data']['result'] = event['result']['resultcommand']
                                #i['data']['command'] = event['result']['cmddata']
                                #print "kkkkkeeeeeeeeeeeeekkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                                #print "kkkkkeeeeeeeeeeeeekkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                                #print "kkkkkeeeeeeeeeeeeekkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                                #self.objectxmpp.send_message( mto=i['to'],
                                            #mbody=json.dumps(i),
                                            #mtype='chat')
                                #self.event.remove(i)
                                ##self.show_eventloop()
                                #break
                    #else:
                        #self.addevent(event)
                        #print "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
                        #print "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
                        #print "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"

                #except TimeoutError:
                    #print "*******************TimeoutError"
 
        #except KeyboardInterrupt:
            #pass
        #finally:
            #print "****************************manage_event end"
            #pass



#{'base64': False,
 #'sessionid': 'commandmrpa8',
 #'ret': 0,
 #'to': 'rspulse@localhost',
 #'_eventype': 'TEVENT',
 #'action': 'applicationdeploymenttest',
 #'data': {'Dtypequery': 'TEVENT', 
          #'Devent': 'Mastereventfinish_sc1bf',
          #'result': {'codeerror': 0, 'resultcommand': 'total 72\n\ndrwxr-xr-x  7 root root  4096 Aug 17 13:48 .\n\ndrwxr-xr-x 14 root root  4096 Aug 17 13:48 ..\n\nlrwxrwxrwx  1 root root    35 Aug 17 13:48 __init__.py -> /usr/share/pyshared/mmc/__init__.py\n\n-rw-r--r--  1 root root   131 Aug 17 13:46 __init__.pyc\n\nlrwxrwxrwx  1 root root    32 Aug 17 13:47 agent.py -> /usr/share/pyshared/mmc/agent.py\n\n-rw-r--r--  1 root root 30701 Aug 17 13:46 agent.pyc\n\ndrwxr-xr-x  2 root root  4096 Aug 17 13:48 client\n\ndrwxr-xr-x  5 root root  4096 Aug 17 13:48 core\n\ndrwxr-xr-x  2 root root  4096 Aug 17 13:47 database\n\ndrwxr-xr-x 17 root root  4096 Aug 17 13:48 plugins\n\nlrwxrwxrwx  1 root root    31 Aug 17 13:47 site.py -> /usr/share/pyshared/mmc/site.py\n\n-rw-r--r--  1 root root   423 Aug 17 13:46 site.pyc\n\nlrwxrwxrwx  1 root root    30 Aug 17 13:48 ssl.py -> /usr/share/pyshared/mmc/ssl.py\n\n-rw-r--r--  1 root root  1453 Aug 17 13:46 ssl.pyc\n\ndrwxr-xr-x  2 root root  4096 Aug 17 13:48 support\n',
                     #'cmddata': 'ls -al'}
          #}
#}

#MESSAGE QUEUE {'base64': False, 'sessionid': 'commandhf1j8', 'ret': 0, 'to': 'rspulse@localhost', '_eventype': 'TEVENT',
               #'action': 'applicationdeploymenttest',
               #'data': {'Dtypequery': 'TEVENT',
                        #'Devent': 'Mastereventstart_m0bis'}}


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
                            'cmddata' in event['data']['result'] and \
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
                                        'command' :  event['data']['result']['cmddata'],
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
                        print "*******SEND MESSAGE************"
                        print "*******SEND MESSAGE************"
                        print "*******SEND MESSAGE************"
                        print "SEND MESSAGE %s"%msg
                        self.objectxmpp.send_message( mto = event['to'],
                                            mbody=json.dumps(msg),
                                            mtype='chat')
                    else:
                        print "*******REGISTER MESSAGE************"
                        print "*******REGISTER MESSAGE************"
                        print "*******REGISTER MESSAGE************"
                        self.addevent(event)

                except TimeoutError:
                    print "*******************TimeoutError"
 
        except KeyboardInterrupt:
            pass
        finally:
            print "****************************manage_event end"
            pass