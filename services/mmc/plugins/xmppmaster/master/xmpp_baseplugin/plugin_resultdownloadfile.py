# -*- coding: utf-8; -*-
from utils import pulginmaster, pulginmastersessionaction
import base64
import json
import os
import zlib
from utils import md5
import hashlib

plugin={"VERSION": "1.1", "NAME" :"resultdownloadfile","TYPE":"serverrelais"}

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

@pulginmastersessionaction("actualise",20)
def action( objetxmpp, action, sessionid, data, message, ret, dataobj, objsessiondata):
    try:
        if ret != 0:
            objetxmpp.event("pluginaction", { 'action': 'transfertfile','sessionid': sessionid,'status': 'start', 'to' : message['from'], 'from' : message['to'] ,'file' : objsessiondata.getdatasession()['whowritefile']})
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
            objetxmpp.event("pluginaction", { 'action': 'transfertfile','sessionid': sessionid, 'status': 'process','size' : sizefile,'to' : message['from'], 'from' : message['to'] ,'file' : objsessiondata.getdatasession()['whowritefile']})
            objetxmpp.send_message( mto=message['from'],
                                mbody=json.dumps(command),
                                mtype='groupchat')
        else:
            md5file =  md5 (objsessiondata.getdatasession()['whowritefile'])
            if md5file == dataobj['md5']:
                objetxmpp.event("pluginaction", { 'action': 'transfertfile','sessionid': sessionid, 'status': 'finished','success':True,  'to' : message['from'], 'from' : message['to'] ,'file' : objsessiondata.getdatasession()['whowritefile']})
            else:
                objetxmpp.event("pluginaction", { 'action': 'transfertfile','sessionid': sessionid, 'status': 'finished','success':False,  'to' : message['from'], 'from' : message['to'] ,'file' : objsessiondata.getdatasession()['whowritefile']})
            objetxmpp.session.clear(sessionid)
    except Exception as e:
        objetxmpp.session.clear(sessionid)
        objetxmpp.event("pluginaction", { 'action': 'transfertfile','sessionid': sessionid,'status': 'error','msgerror' :str(e) , 'to' : message['from'], 'from' : message['to'] ,'file' : objsessiondata.getdatasession()['whowritefile']})
