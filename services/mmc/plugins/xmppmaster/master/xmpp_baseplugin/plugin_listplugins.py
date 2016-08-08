import base64
import json
import subprocess


plugin={"VERSION": "1.0", "NAME" :"listplugins"}


def action(jsonobj, msg, classxmpp ):
    
    
    result = { 'action': "result%s"%jsonobj['action'],
               'msg' : 'Error : plugin_listplugins'}
             #'data' : 'resultat test plugin getipinfo'}
    sessionid = ''
    try:
        if jsonobj['sessionid'] != "":
            sessionid= jsonobj['sessionid']
    except:
        sessionid = "result"
    #print json.dumps(er.messagejson, indent=4, sort_keys=True)
    classxmpp.send_message( mto=msg['from'],
                            mbody=result,
                            mtype='chat')

    #print json.dumps(jsonobj, indent=4, sort_keys=True)
    
    #classxmpp.send_message( mto=msg['from'],
                            #mbody=json.dumps(result),
                            #mtype='chat')