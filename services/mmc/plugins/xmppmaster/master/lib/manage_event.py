#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016-2017 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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

import json
from multiprocessing import TimeoutError
import threading
from utils import getRandomName, call_plugin
from sleekxmpp import jid
import logging

logger = logging.getLogger()


class manage_event:
    def __init__(self, queue_in, objectxmpp):
        self.event = []
        self.queue_in = queue_in
        self.namethread = getRandomName(5, "threadevent")
        self.objectxmpp = objectxmpp
        self.threadevent = threading.Thread(
            name=self.namethread, target=self.manage_event_command)
        self.threadevent.start()
        logging.info('manage event start')

    def show_eventloop(self):
        print "boucle evenement"
        for i in self.event:
            print '------------\n%s\n------------' % i

    def addevent(self, event):
        self.event.append(event)

    def delevent(self, event):
        self.event.append(event)

    @staticmethod
    def create_TEVENT(to, action, sessionid, devent):
        return {
            'to': to,
            'action': action,
            'sessionid': sessionid,
            'data': {'Dtypequery': 'TEVENT', 'Devent': devent},
            'ret': 0,
            'base64': False,
            '_eventype': 'TEVENT'
        }

    @staticmethod
    def create_EVENT(to, action, sessionid, Dtypequery,
                     devent, ret=0, base64=False):
        return {
            'to': to,
            'action': action,
            'sessionid': sessionid,
            'data': {'Dtypequery': 'TR', 'Devent': devent},
            'ret': ret,
            'base64': base64
        }

    @staticmethod
    def create_EVENT_TR(to, action, sessionid, devent):
        return {
            'to': to,
            'action': action,
            'sessionid': sessionid,
            'data': {'Dtypequery': 'TR', 'Devent': devent},
            'ret': 0,
            'base64': False
        }

    @staticmethod
    def create_EVENT_ERR(to, action, sessionid, devent):
        return {
            'to': to,
            'action': action,
            'sessionid': sessionid,
            'data': {'Dtypequery': 'TE', 'Devent': devent},
            'ret': 125,
            'base64': False
        }

    def manage_event_loop(self):
        # traitement message interne
        for i in self.event:
            if not 'event' in i:
                # message de type loop
                jidto = jid.JID(str(i['to'])).bare
                msg = {
                    'from': jidto,
                    'to': jidto,
                    'body': {
                        'ret': i['ret'],
                        'sessionid': i['sessionid'],
                        'base64': False
                    }
                }
                if self.objectxmpp.session.isexist(
                        i['sessionid']) and jidto == self.objectxmpp.boundjid.bare:
                    # call plugin i['sessionid'] == msg['from'].bare
                    call_plugin(i['action'],
                                self.objectxmpp,
                                i['action'],
                                i['sessionid'],
                                i['data'],
                                msg,
                                {}
                                )

    def delmessage_loop(self, devent):
        # supprime message loop devent
        for i in self.event:
            if not 'event' in i:
                if i['data']['Devent'] == devent:
                    self.event.remove(i)
                    break

    def delmessage_loop_Dtypequery(self, Dtypequery):
        # supprime message loop devent
        for i in self.event:
            if not 'event' in i:
                if i['data']['Dtypequery'] == Dtypequery:
                    self.event.remove(i)
                    break

    def clear(self, sessionid):
        self.event = [x for x in self.event if x['sessionid'] != sessionid]

    def manage_event_command(self):
        logging.info('loop event wait start')
        try:
            while True:
                try:
                    # lit event
                    event = self.queue_in.get(5)
                    if event == "quit":
                        break
                    if 'eventMessageraw' in event:
                        message = event['eventMessageraw']
                        recipientsucces = message['data']['tosucces']
                        recipienterror = message['data']['toerror']
                        del message['data']['tosucces']
                        del message['data']['toerror']
                        if recipienterror != None and message['data']['codeerror'] != 0:
                            del message['data']['codeerror']
                            self.objectxmpp.send_message(mto=recipienterror,
                                                         mbody=json.dumps(
                                                             message),
                                                         mtype='chat')
                        elif recipientsucces != None:
                            del message['data']['codeerror']
                            self.objectxmpp.send_message(mto=recipientsucces,
                                                         mbody=json.dumps(
                                                             message),
                                                         mtype='chat')

                        if 'data' in event['eventMessageraw'] and 'descriptor' in event['eventMessageraw'][
                                'data'] and 'sequence' in event['eventMessageraw']['data']['descriptor']:
                            # search workingstep for message log to log service
                            # et log to syslog
                            if 'stepcurrent' in event['eventMessageraw']['data']:
                                nb_currentworkingset = int(
                                    event['eventMessageraw']['data']['stepcurrent']) - 1
                                for i in event['eventMessageraw']['data']['descriptor']['sequence']:
                                    if int(i['step']) == nb_currentworkingset:
                                        logging.debug(
                                            'deploy [process command : %s ]\n%s' %
                                            (event['eventMessageraw']['sessionid'], json.dumps(
                                                i, indent=4, sort_keys=True)))
                                        if 'command' in i:
                                            if i['codereturn'] == 0:
                                                color = "green"
                                            else:
                                                color = "red"

                                            self.objectxmpp.xmpplog('[%s]-[%s]:<span style="color: %s;"> '\
                                                                        '[Process command] errorcode %s for'\
                                                                        'command : %s <span>' % (event['eventMessageraw']['data']['name'],
                                                                                                    i['step'],
                                                                                                    color,
                                                                                                    i['codereturn'],
                                                                                                    i['command'][:20]),
                                                                        type = 'deploy',
                                                                        sessionname = event['eventMessageraw']['sessionid'],
                                                                        priority = i['step'],
                                                                        action = "",
                                                                        who = self.objectxmpp.boundjid.bare,
                                                                        how = "",
                                                                        why = "",
                                                                        module = "Deployment | Error | Execution",
                                                                        date = None ,
                                                                        fromuser = event['eventMessageraw']['data']['login'],
                                                                        touser = "")
                                        else:
                                            self.objectxmpp.xmpplog('[%s]: %s ' % (i['step'], i['action']),
                                                                    type = 'deploy',
                                                                    sessionname = event['eventMessageraw']['sessionid'],
                                                                    priority = i['step'],
                                                                    action = "",
                                                                    who = self.objectxmpp.boundjid.bare,
                                                                    how = "",
                                                                    why = "",
                                                                    module = "Deployment | Execution",
                                                                    date = None ,
                                                                    fromuser = event['eventMessageraw']['data']['login'],
                                                                    touser = "")
                                        break
                        continue

                    self.show_eventloop()
                    if 'sessionid' in event and '_eventype' in event:
                        if 'result' in event['data'] and \
                            'command' in event['data']['result'] and \
                            'codeerror' in event['data']['result'] and \
                            'Dtypequery' in event['data']['result'] and \
                                'Devent' in event['data']['result']:
                            msg = {
                                'ret': event['ret'],
                                'sessionid': event['sessionid'],
                                'base64': event['base64'],
                                'action': event['action'],
                                'data': {
                                    'resultcommand': event['data']['result']['resultcommand'],
                                    'command': event['data']['result']['command'],
                                    'codeerror': event['data']['result']['codeerror'],
                                    'Dtypequery': event['data']['Dtypequery'],
                                    'Devent': event['data']['Devent']
                                }
                            }
                        else:
                            msg = {
                                'ret': event['ret'],
                                'sessionid': event['sessionid'],
                                'base64': event['base64'],
                                'action': event['action'],
                                'data': {
                                    'Dtypequery': event['data']['Dtypequery'],
                                    'Devent': event['data']['Devent']
                                }
                            }
                        self.objectxmpp.send_message(mto=event['to'],
                                                     mbody=json.dumps(msg),
                                                     mtype='chat')
                    else:
                        if 'sessionid' in event:
                            event['data'] = dict(
                                self.objectxmpp.session.sessionfromsessiondata(
                                    event['sessionid']).datasession.items() +
                                event['data'].items())
                        self.addevent(event)
                except TimeoutError:
                    print "TimeoutError"

        except KeyboardInterrupt:
            pass
        finally:
            logging.info('loop event wait stop')
