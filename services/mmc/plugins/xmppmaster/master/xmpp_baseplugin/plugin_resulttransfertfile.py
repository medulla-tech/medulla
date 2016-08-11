# -*- coding: utf-8; -*-
from utils import pulginmaster, pulginmastersessionaction
import base64
import json
import os
import zlib
from utils import md5
import hashlib

plugin={"VERSION": "1.0", "NAME" :"resulttransfertfile","TYPE":"relayserver"}

@pulginmastersessionaction("actualise",20)
def action( objetxmpp, action, sessionid, data, message, ret, dataobj, objsessiondata):
    try:
        sessiondata = objetxmpp.session.sessionfromsessiondata(sessionid)
        namefile = sessiondata.getdatasession()['qui']

        if dataobj['end']:
            objetxmpp.event("pluginaction", { 'action': 'transfertfile','sessionid': sessionid, 'status': 'finished','success':True,  'to' : message['from'], 'from' : message['to'] ,'file' : sessiondata.getdatasession()['qui']})
            objetxmpp.session.clear(sessionid)
            return
        if ret != 0:
            objetxmpp.event("pluginaction", { 'action': 'transfertfile','sessionid': sessionid,'status': 'finished','success':False, 'to' : message['from'], 'from' : message['to'] ,'file' : sessiondata.getdatasession()['qui']})
            objetxmpp.session.clear(sessionid)
            return

        command = {
            'action' : 'transfertfile',
            'base64' : False,
            'sessionid': sessionid,
            'data' : ''
        }
        result={}
        try:
            part =  sessiondata.getdatasession()['part']
        except:
            objetxmpp.event("pluginaction", { 'action': 'transfertfile','sessionid': sessionid,'status': 'start', 'to' : message['from'], 'from' : message['to'] ,'file' : sessiondata.getdatasession()['qui']})
            sessiondata.datasession['part'] = 0
            sessiondata.datasession['pointeur'] = 0
        pointeur =  sessiondata.getdatasession()['pointeur']
        part =  sessiondata.getdatasession()['part']
        try :
            f = open( namefile, "rb")
            f.seek(pointeur, 0)
            buffer = f.read(25000)
            sessiondata.datasession['pointeur'] = f.tell()
            objetxmpp.event("pluginaction", { 'action': 'transfertfile','sessionid': sessionid,'status': 'process','size': sessiondata.getdatasession()['pointeur'], 'to' : message['from'], 'from' : message['to'] ,'file' : sessiondata.getdatasession()['qui']})
            objetxmpp.session.affiche()
        except IOError:
            objetxmpp.event("pluginaction", { 'action': 'transfertfile','sessionid': sessionid,'status': 'error','msgerror' :'IOError' ,'size': sessiondata.getdatasession()['pointeur'], 'to' : message['from'], 'from' : message['to'] ,'file' : sessiondata.getdatasession()['qui']})
            raise
        finally:
            f.close()
        sessiondata.datasession['part'] = part + 1
        command['md5trame'] = hashlib.md5(buffer).hexdigest()
        if len(buffer)== 0 or buffer == "":
            command['end'] = True
            command['md5trame'] = md5(namefile)
        else:
            command['end'] = False
            aaa = zlib.compress(buffer)
            command['data'] = base64.b64encode(aaa)
        objetxmpp.send_message( mto=message['from'],
                                mbody=json.dumps(command),
                                mtype='chat')
    except Exception as e:
        print "erreur %s"%str(e)
        objetxmpp.event("pluginaction", { 'action': 'transfertfile','sessionid': sessionid,'status': 'error','msgerror' :str(e) ,'size': sessiondata.getdatasession()['pointeur'], 'to' : message['from'], 'from' : message['to'] ,'file' : sessiondata.getdatasession()['qui']})
