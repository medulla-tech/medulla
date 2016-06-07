# -*- coding: utf-8 -*-
#import base64
import json
import platform, sys, os
from  lib.utils import file_get_content, file_put_content, typelinux, servicelinuxinit, isprogramme, simplecommande

from lib.networkinfo import networkagentinfo
plugin={"VERSION": "1.0", "NAME" :"updatehostname"}

def action( objetxmpp, action, sessionid, data, message, dataerreur ):
    print "plugin updatehostname"
    reponse={}
    if action == 'updatehostname':
        resultaction = "result%s"%action
        dataerreur['action'] = resultaction
        dataerreur['data']['msg'] = "ERROR : updatehostname"
        dataerreur['sessionid'] = sessionid
        try:
            reponse['action'] = resultaction
            reponse['ret'] = 0
            reponse['sessionid'] = sessionid
            reponse['base64'] = False
            reponse['data'] = {}
            #change hostname
            if sys.platform.startswith('linux'):
                # change hostname debian
                if isprogramme("hostnamectl"):
                    obj = simplecommande("hostnamectl set-hostname %s"%data['hostname'])
                    if int(obj['code']) != 0:
                        dataerreur['ret']=int(obj['code'])
                        dataerreur['data']['msg'] = "ERROR : updatehostname %s"% obj['result']
                        raise
                else:
                    print "non hostnamectl"
                    if os.path.isfile("/etc/hostname"):
                        aa = file_get_content("/etc/hostname")
                        aa = aa.strip( "\n\r\t " )
                        file_put_content("/etc/hostname",data['hostname'])
                        inputFile = open("/etc/hosts", 'rb')
                        contenue = inputFile.read()
                        inputFile.close()
                        newcontenue = contenue.replace(aa,data['hostname'])
                        inputFile = open("/etc/hosts", 'wb')
                        inputFile.write(newcontenue)
                        inputFile.close()
                        if typelinux() == "init":
                            if isprogramme("hostname.sh"):
                                servicelinuxinit('hostname.sh','restart')
                            elif isprogramme("hostname"):
                                simplecommande("service hostname start")
                            else:
                                dataerreur['data']['msg'] = "ERROR : ne sait pas changer hostname sur ce systeme"
                                reponse['ret']=255
                                raise
            elif sys.platform.startswith('win'):
                obj=simplecommande("netdom renamecomputer %COMPUTERNAME% /Newname \"%s\""%data['hostname']) 
                if int(obj['code']) != 0:
                    dataerreur['ret']=int(obj['code'])
                    dataerreur['data']['msg'] = "ERROR : updatehostname %s"% obj['result']
                    raise
            elif sys.platform.startswith('darwin'):
                obj=simplecommande("scutil –-set HostName %s"%data['hostname'])
                if int(obj['code']) != 0:
                    dataerreur['ret']=int(obj['code'])
                    dataerreur['data']['msg'] = "ERROR : updatehostname %s"% obj['result']
                    raise
            else:
                dataerreur['ret']=255
                dataerreur['data']['msg'] = "ERROR : updatehostname OS Pas pris en charge"
                raise
        except:
            objetxmpp.send_message( mto=message['from'],
                                    mbody=json.dumps(dataerreur),
                                    mtype='chat')
            return
        #print json.dumps(netinfo.messagejson, indent=4, sort_keys=True)

        objetxmpp.send_message( mto=message['from'],
                                mbody=json.dumps(reponse),
                                mtype='chat')
