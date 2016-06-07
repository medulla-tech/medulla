#import base64
import json
#import subprocess
#from lib.network import networkagent
from lib.networkinfo import networkagentinfo
plugin={"VERSION": "1.0", "NAME" :"getipinfo"}

def action( objetxmpp, action, sessionid, data, message, dataerreur ):
    print "plugin getipinfo"
    
    if action == 'getipinfo':
        resultaction = "result%s"%action
        dataerreur['action'] = resultaction
        dataerreur['data']['msg'] = "ERROR : getipinfo"
        dataerreur['sessionid'] = sessionid
        
        if not isinstance(data,list):
            dataerreur['data']['msg'] = "ERROR : getipinfo list mac adress"
            objetxmpp.send_message( mto=message['from'],
                                    mbody=json.dumps(dataerreur),
                                    mtype='chat')
            return
      
        strip_list = [item.strip("\n\t\"'") for item in data]

        try:
            
            netinfo = networkagentinfo(sessionid, resultaction, strip_list)
            
            del netinfo.messagejson['dhcp']
            del netinfo.messagejson['dnshostname']
            del netinfo.messagejson['listdns']
            netinfo.messagejson['data']={}
            if len(netinfo.messagejson['listipinfo'])==0:
                netinfo.messagejson['data']['msg']="interface missing"
                netinfo.messagejson['ret']=255
            else:
                netinfo.messagejson['data']['listipinfo']=netinfo.messagejson['listipinfo']
                netinfo.messagejson['ret']=0
                for t in netinfo.messagejson['data']['listipinfo']:
                    del t['broadcast']
                    del t['dhcpserver']

            del netinfo.messagejson['listipinfo']
            
            del netinfo.messagejson['msg']
            #netinfo = networkagent(sessionid, resultaction, strip_list)
        except:
            objetxmpp.send_message( mto=message['from'],
                                    mbody=json.dumps(dataerreur),
                                    mtype='chat')

        #print json.dumps(netinfo.messagejson, indent=4, sort_keys=True)
        objetxmpp.send_message( mto=message['from'],
                                mbody=json.dumps(netinfo.messagejson),
                                mtype='chat')
