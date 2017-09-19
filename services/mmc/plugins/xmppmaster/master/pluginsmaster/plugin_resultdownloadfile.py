# -*- coding: utf-8; -*-
from utils import pluginmaster, pluginmastersessionaction
import base64
import json
import os
import zlib
from utils import md5
import hashlib

def writefileappend(name, data):
    try:
        file = open(name, "ab")
        file.write(data)
        pointeur = file.tell()
        file.close()
        return pointeur
    except Exception as e:
        print str(e)

def delfile(name):
    try:
        print "renove %s"%name
        os.remove(name)
    except Exception as e:
        print "renove %s  : %s"%(name, str(e))

@pluginmastersessionaction("actualise",20)
def action( xmppobject, action, sessionid, data, message, ret, dataobj, objsessiondata):
    try:
        if ret != 0:
            xmppobject.event("pluginaction", { 'action': 'transferfile','sessionid': sessionid,'status': 'start', 'to' : message['from'], 'form' : message['to'] ,'file' : objsessiondata.getdatasession()['whowritefile']})
            return
        if dataobj['end'] == True:
            data1 = ""
        else:
            data = base64.b64decode(data)
            data1 = zlib.decompress(data)
            md5trame = hashlib.md5(data1).hexdigest()
            if md5trame != dataobj['trame']:
                raise
        if dataobj['part'] == 0 and objsessiondata.getdatasession()['whowritefile'] != "":
            delfile(objsessiondata.getdatasession()['whowritefile'])

        sizefile = writefileappend(objsessiondata.getdatasession()['whowritefile'], data1)
        if dataobj['end'] == False:
            command={
                'action' : 'downloadfile',
                'base64' : False,
                'sessionid': sessionid,
                'data' : ''
            }
            xmppobject.event("pluginaction", { 'action': 'transferfile','sessionid': sessionid, 'status': 'process','size' : sizefile,'to' : message['from'], 'form' : message['to'] ,'file' : objsessiondata.getdatasession()['whowritefile']})
            xmppobject.send_message( mto=message['from'],
                                mbody=json.dumps(command),
                                mtype='chat')
        else:
            md5file =  md5 (objsessiondata.getdatasession()['whowritefile'])
            if md5file == dataobj['md5']:
                xmppobject.event("pluginaction", { 'action': 'transferfile','sessionid': sessionid, 'status': 'finished','success':True,  'to' : message['from'], 'form' : message['to'] ,'file' : objsessiondata.getdatasession()['whowritefile']})
            else:
                xmppobject.event("pluginaction", { 'action': 'transferfile','sessionid': sessionid, 'status': 'finished','success':False,  'to' : message['from'], 'form' : message['to'] ,'file' : objsessiondata.getdatasession()['whowritefile']})
            xmppobject.session.clear(sessionid)
    except Exception as e:
        xmppobject.session.clear(sessionid)
        xmppobject.event("pluginaction", { 'action': 'transferfile','sessionid': sessionid,'status': 'error','msgerror' :str(e) , 'to' : message['from'], 'form' : message['to'] ,'file' : objsessiondata.getdatasession()['whowritefile']})

