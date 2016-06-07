#import base64
import json
import platform, sys, os
#import subprocess
#from lib.network import networkagent
from lib.networkinfo import networkagentinfo

plugin={"VERSION": "1.0", "NAME" :"gethostnameinfo"}

def action( objetxmpp, action, sessionid, data, message, dataerreur ):
    print "plugin gethostnameinfo"
    reponse={}
    if action == 'gethostnameinfo':
        resultaction = "result%s"%action
        dataerreur['action'] = resultaction
        dataerreur['data']['msg'] = "ERROR : gethostnameinfo"
        dataerreur['sessionid'] = sessionid
        try:
            reponse['action'] = resultaction
            reponse['ret'] = 0
            reponse['sessionid'] = sessionid    
            reponse['base64'] = False
            reponse['data'] = {}
            reload(platform)
            reponse['data']['hostname'] = platform.node()
        except:
            objetxmpp.send_message( mto=message['from'],
                                    mbody=json.dumps(dataerreur),
                                    mtype='chat')
            return

        #print json.dumps(netinfo.messagejson, indent=4, sort_keys=True)
        objetxmpp.send_message( mto=message['from'],
                                mbody=json.dumps(reponse),
                                mtype='chat')
    