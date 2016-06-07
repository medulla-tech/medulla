import base64
import json
import subprocess


plugin={"VERSION": "1.0", "NAME" :"restartbot"}

def action( objetxmpp, action, sessionid, data, message, dataerreur ):
    print 'plugin restartbot'
    reponse={}
    if action == 'restartbot':
        resultaction = "result%s"%action
        reponse['action'] = resultaction    
        reponse['sessionid'] = sessionid    
        reponse['base64'] = False
        reponse['ret'] = 0
        reponse['data'] = {}
        reponse['data']['msg']="restart %s"%message['to']
        #print json.dumps(er.messagejson, indent=4, sort_keys=True)
        objetxmpp.send_message( mto=message['from'],
                                mbody=json.dumps(reponse),
                                mtype='chat')
        objetxmpp.restartBot()
    