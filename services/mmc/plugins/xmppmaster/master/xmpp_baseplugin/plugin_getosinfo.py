#import base64
import json
import os, sys
import platform
#import subprocess
#from lib.network import networkagent


plugin={"VERSION": "1.0", "NAME" :"getosinfo"}

debiandist = ['astra', 'canaima', 'collax', 'cumulus', 'damn', 'debian', 'doudoulinux', 'euronode', 'finnix', 'grml', 'kanotix', 'knoppix', 'linex', 'linspire',   'advanced', 'lmde', 'mepis','ocera', 'ordissimo','parsix', 'pureos', 'rays', 'aptosid', 'ubuntu', 'univention', 'xandros']

redhadlist=['centos', 'rhel', 'redhat', 'fedora', 'mageia','mga', 'mandiva', 'suse', 'oracle', 'scientific', 'fermi']

def action( objetxmpp, action, sessionid, data, message, dataerreur ):
    print "plugin getosinfo"
    reponse={}
    if action == 'getosinfo':
        resultaction = "result%s"%action
        dataerreur['action'] = resultaction
        dataerreur['data']['msg'] = "ERROR : getosinfo"
        dataerreur['sessionid'] = sessionid
        try:
            reponse['action'] = resultaction    
            reponse['sessionid'] = sessionid    
            reponse['base64'] = False
            reponse['data'] = {}
            reponse['data']['distro_type'] = 2
            reponse['data']['name'] = platform.platform()
            if sys.platform.startswith('linux'):
                reponse['data']['family'] = "linux"
                val=platform.platform().lower()
                for t in debiandist:
                    if t in val:
                        reponse['data']['distro_type'] = 1
                        break;
                #if  reponse['data']['distro_type'] == 0:   
                    #for  t in redhadlist:       
                        #if t in val:
                            #reponse['data']['distro_type'] = 2
                            #break;
            elif sys.platform.startswith('win'):
                reponse['data']['family'] = "windows"
            elif sys.platform.startswith('darwin'):
                reponse['data']['family'] = "macos"
            reponse['data']['version'] = platform.release()   
            UnameSystem = platform.uname()
            reponse['data']['distro_name'] = UnameSystem[3]
        except:
            objetxmpp.send_message( mto=message['from'],
                                    mbody=json.dumps(dataerreur),
                                    mtype='chat')

        #print json.dumps(netinfo.messagejson, indent=4, sort_keys=True)
        objetxmpp.send_message( mto=message['from'],
                                mbody=json.dumps(reponse),
                                mtype='chat')
    