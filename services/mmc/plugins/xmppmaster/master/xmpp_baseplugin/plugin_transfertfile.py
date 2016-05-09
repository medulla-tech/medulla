# -*- coding: utf-8; -*-
import json
import base64
import zlib
import hashlib
from lib.utils import  simplecommandestr, simplecommande, md5
import sys, os, platform
from  lib.utils import pulginprocess
from lib.managesession import sessiondatainfo, session

plugin={"VERSION": "1.0", "NAME" :"transfertfile"}

def writefileappend(name, data):
    try:
        file = open(name, "ab")
        file.write(data)
        file.close()
    except Exception as e:
        print str(e)

def delfile(name):
    try:
        print "renove %s"%name
        os.remove(name)
    except Exception as e:
        print str(e)

@pulginprocess
def action( objetxmpp, action, sessionid, data, message, dataerreur, result):
    #todo add event 
    
    result['end'] = False
    try:
        if not objetxmpp.session.isexist(sessionid):
            datasession={
                            'ou' : data['ou']
                        }
            objetxmpp.session.createsessiondatainfo(sessionid, datasession, 10)
            delfile(data['ou'])
            result['base64'] = False
            result['part'] = 0
            objetxmpp.event("pluginaction", {   'action': action,
                                                'sessionid': sessionid,
                                                'status': 'start', 
                                                'to' : message['from'],
                                                'form' : message['to'] ,
                                                'file' : data['ou']})
            return
        else:
            objetxmpp.session.reactualisesession(sessionid)

 
        objetxmpp.session.affiche()
        sessiondata = objetxmpp.session.sessionfromsessiondata(sessionid)
        if dataobj['end'] == False:
            data = base64.b64decode(data)
            data1 = zlib.decompress(data)
            md5trame = hashlib.md5(data1).hexdigest()
            objetxmpp.event("pluginaction", { 'action': action,
                            'sessionid': sessionid,
                            'status': 'process',
                            'to' : message['from'],
                            'form' : message['to'] ,
                            'file' : sessiondata.getdatasession()['ou']})
            if md5trame != dataobj['md5trame']:
                objetxmpp.event("pluginaction", { 'action': action,
                            'sessionid': sessionid,
                            'status': 'error',
                            'msgerror' : "transfert error",
                            'to' : message['from'],
                            'form' : message['to'] ,
                            'file' :  sessiondata.getdatasession()['ou']})
                raise
            writefileappend(sessiondata.getdatasession()['ou'], data1)
        else:
            md5trame =  md5 (sessiondata.getdatasession()['ou'])
            if md5trame != dataobj['md5trame']:
                dataerreur['ret'] = 255
                dataerreur['msg'] = "transfert error"
                objetxmpp.event("pluginaction", { 'action': action,
                            'sessionid': sessionid,
                            'status': 'error',
                            'msgerror' : "transfert error",
                            'to' : message['from'],
                            'form' : message['to'] ,
                            'file' : sessiondata.getdatasession()['ou']})
                raise
            result['end'] = True
            objetxmpp.event("pluginaction", { 'action': action,
                            'sessionid': sessionid,
                            'status': 'finished', 
                            'success': True,
                            'to' : message['from'],
                            'form' : message['to'] ,
                            'file' :  sessiondata.getdatasession()['ou']})
            objetxmpp.session.clear(sessionid)
    except Exception as e:
        print "exception %s" % str(e)
