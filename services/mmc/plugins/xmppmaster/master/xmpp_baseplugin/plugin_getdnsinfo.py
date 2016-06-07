#import base64
import json
#import subprocess
#from lib.network import networkagent
from lib.networkinfo import networkagentinfo
plugin={"VERSION": "1.0", "NAME" :"getdnsinfo"}

def action( objetxmpp, action, sessionid, data, message, dataerreur ):
    print "plugin getdnsinfo"
    
    if action == 'getdnsinfo':
        resultaction = "result%s"%action
        dataerreur['action'] = resultaction
        dataerreur['data']['msg'] = "ERROR : process getdnsinfo"
        dataerreur['sessionid'] = sessionid
        try:
            netinfo = networkagentinfo(sessionid, resultaction, [])
            del netinfo.messagejson['dhcp']
            del netinfo.messagejson['dnshostname']
            #del netinfo.messagejson['listdns']
            netinfo.messagejson['data']={}
            del netinfo.messagejson['listipinfo']
            netinfo.messagejson['data']['listdns']=netinfo.messagejson['listdns']
            netinfo.messagejson['ret']=0            
            del netinfo.messagejson['msg']
            del netinfo.messagejson['listdns']
        except:
            objetxmpp.send_message( mto=message['from'],
                                    mbody=json.dumps(dataerreur),
                                    mtype='chat')

        #print json.dumps(netinfo.messagejson, indent=4, sort_keys=True)
        objetxmpp.send_message( mto=message['from'],
                                mbody=json.dumps(netinfo.messagejson),
                                mtype='chat')
