import base64
import json
import subprocess

from lib.networkinfo import networkagentinfo
plugin={"VERSION": "1.0", "NAME" :"installlib","TYPE":"all"}

def action(jsonobj, msg, classxmpp ):
    
    
    result = { 'action': "result%s"%jsonobj['action'],
               'msg' : 'Error : plugin_getipinfo'}
             #'data' : 'resultat test plugin getipinfo'}
    sessionid = ''
    try:
        if jsonobj['sessionid'] != "":
            sessionid= jsonobj['sessionid']
    except:
        sessionid = "result"
   
    try:
        if isinstance(jsonobj['param'],str) or isinstance(jsonobj['param'],unicode) :
            jsonobj['param']=[jsonobj['param']]

    except NameError:
        jsonobj['param']=[]
    
    try:
        er = networkagentinfo(sessionid,"result%s"%jsonobj['action'],jsonobj['param'])
    except:
        classxmpp.send_message( mto=msg['from'],
                            mbody=json.dumps(result),
                            mtype='chat')
    
    #print json.dumps(er.messagejson, indent=4, sort_keys=True)
    classxmpp.send_message( mto=msg['from'],
                            mbody=json.dumps(er.messagejson),
                            mtype='chat')

    #print json.dumps(jsonobj, indent=4, sort_keys=True)
    
    #classxmpp.send_message( mto=msg['from'],
                            #mbody=json.dumps(result),
                            #mtype='chat')