#import base64
import json
import sys, platform, os
#import subprocess
#from lib.network import networkagent
#from lib.networkinfo import networkagentinfo

from  lib.utils import file_get_content, file_put_content, typelinux, servicelinuxinit, isprogramme, simplecommande
plugin={"VERSION": "1.0", "NAME" :"updatednsinfo"}

def action( objetxmpp, action, sessionid, data, message, dataerreur ):
    print "plugin updatednsinfo"
    reponse={}
    if action == 'updatednsinfo':
        resultaction = "result%s"%action
        dataerreur['action'] = resultaction
        dataerreur['data']['msg'] = "ERROR : updatednsinfo"
        dataerreur['sessionid'] = sessionid
        try:
            reponse['action'] = resultaction
            reponse['ret'] = 0
            reponse['sessionid'] = sessionid
            reponse['base64'] = False
            reponse['data'] = {}
            if not isinstance(data['listdns'],list):
                dataerreur['data']['msg'] = "ERROR : updatednsinfo list dns"
                raise
            strip_list = [item.strip("\n\t\"'") for item in data['listdns']]

            if sys.platform.startswith('linux'):

                if os.path.isfile("/etc/resolvconf/resolv.conf.d/head"):
                    a = file_get_content("/etc/resolvconf/resolv.conf.d/head")
                    #file_put_content("/etc/resolvconf/resolv.conf.d/head", "#dns eva\n")
                    for t in strip_list: #resolvconf
                        if t in a:
                            continue
                        else:
                            file_put_content("/etc/resolvconf/resolv.conf.d/head", "nameserver %s\n"%t,"a")
                    
                elif os.path.isfile("/etc/resolv.conf"):
                    a = file_get_content("/etc/resolv.conf")
                    for t in strip_list:
                        if t in a:
                            continue
                        else:
                            file_put_content("/etc/resolv.conf", "nameserver\t%s\n"%t,"a")
                if os.path.isfile("/etc/init.d/networking"):
                    print simplecommande("/etc/init.d/networking restart")
                elif os.path.isfile("/etc/init.d/network"):
                    print simplecommande("/etc/init.d/network restart")
            elif sys.platform.startswith('win'):
                    #set dnsservers name="Local Area Connection" source=dhcp
                    #set dnsservers "Local Area Connection" static 192.168.1.1 primary
                    #set dnsservers "Local Area Connection" static 192.168.1.1 secondary
                for index,t in enumerate(strip_list):
                    print simplecommande("netsh interface ip add dns name=\"Local Area Connection\" addr=%s index=%d"%(t,index+1))
                    ##primaire et secondaire
                    ###netsh interface ip set dns name="Local Area Connection" source=dhcp
                    #netsh interface ip add dns name="Local Area Connection" 8.8.8.8
                    #Pour remettre les DNS en dynamique :netsh dnsclient delete dnsservers %nomCarteReseau% all
                    
            else:
                dataerreur['data']['msg'] = "ERROR : updatednsinfo pas pris encore en compte"   
                dataerreur['ret']=255
                raise


        except:
            objetxmpp.send_message( mto=message['from'],
                                    mbody=json.dumps(dataerreur),
                                    mtype='groupchat')
            return
       
        #print json.dumps(netinfo.messagejson, indent=4, sort_keys=True)
        objetxmpp.send_message( mto=message['from'],
                                mbody=json.dumps(reponse),
                                mtype='groupchat')
