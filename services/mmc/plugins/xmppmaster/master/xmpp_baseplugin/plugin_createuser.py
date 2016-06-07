# -*- coding: utf-8 -*-
import json
import sys, platform, os
from lib.networkinfo import updatedns
from  lib.utils import file_get_content, file_put_content, typelinux, servicelinuxinit, isprogramme, simplecommande, simplecommandestr, CreateWinUser


plugin={"VERSION": "1.0", "NAME" :"createuser"}


def action( objetxmpp, action, sessionid, data, message, dataerreur ):
    print "plugin createuser"
    reponse={}
    if action == 'createuser':
        resultaction = "result%s"%action
        dataerreur['action'] = resultaction
        dataerreur['data']['msg'] = "Erreur createuser"
        dataerreur['sessionid'] = sessionid
        dataerreur['ret'] = 255
        warning = False
        try:
            reponse['action'] = resultaction
            reponse['ret'] = 0
            reponse['sessionid'] = sessionid
            reponse['base64'] = False
            reponse['data'] = {}
            if sys.platform.startswith('linux'):
                #verification user existe
                obj = simplecommandestr("getent passwd  %s"%data['login'])
                if obj['result'] == "":
                    #utilisateur n existe pas -> creation                    
                    obj = simplecommandestr("useradd %s"%data['login'])                    
                    if int(obj['code']) != 0:
                        dataerreur['data']['msg'] = "ERROR : createuser creation user %s  %s"%(data['login'],obj['result'])
                        dataerreur['ret'] = int(obj['code'])
                        raise
                #verification si group exist
                obj = simplecommandestr("getent group %s"%data['group'])                
                if obj['result'] == "":
                    #le group n'existe pas il faut le créer
                    obj = simplecommandestr("groupadd %s"%data['group'])
                    if int(obj['code']) != 0:
                        dataerreur['data']['msg'] = "Warning : creation groupe %s impossible : %s\n"%(data['group'],obj['result'])
                        dataerreur['ret'] = int(obj['code'])
                        warning = true
                if  data['login'] != data['group']:                    
                    #on applique l'utilisateur au groupe 
                    print "applique"
                    obj = simplecommandestr("usermod -a -G %s %s"%(data['group'],data['login']))
                    if int(obj['code']) != 0:
                        dataerreur['data']['msg'] = "%s\nWarning : appliquation groupe %s a utilisateur %s :[%s]"%(dataerreur['data']['msg'], data['group'],data['login'],obj['result'] )
                        warning = true
                # appliquer pawword                
                obj = simplecommandestr("echo '%s:%s'|chpasswd" %(data['login'],data['password']))
                if int(obj['code']) != 0:
                        dataerreur['data']['msg'] = "\n%sWarning : appliquation groupe %s a utilisateur %s :[%s]"%(dataerreur['data']['msg'], data['group'],data['login'],obj['result'] )
                        warning = true
                # appliquer password samba
                    #simplecommande("echo -e \"new_password\nnew_password\" | (smbpasswd -a -s %s)"%data['password'])
                    ###http://www.cyberciti.biz/faq/adding-a-user-to-a-samba-smb-share/
                                #"domain"
                if warning:
                    raise
            elif sys.platform.startswith('win'):
                ##http://support-fr.org/dim/2015/05/18/batch-user-add/
                #CreateWinUser(data['login'],data['password'],[data['group']])
                obj = simplecommandestr("net user %s %s /add" %(data['login'],data['password']))
                if int(obj['code']) != 0:
                    dataerreur['data']['msg'] = "ERROR : compte erreur creation"%(obj['result'])
                    raise
                dataerreur['data']['msg'] =""
                obj = simplecommandestr("net localgroup %s /add" %(data['group']))
                if int(obj['code']) != 0:
                    dataerreur['data']['msg'] = "%s erreur creation compte %s"%(dataerreur['data']['msg'],obj['result'])
                    warning = true
                obj = simplecommandestr("net localgroup %s %s /add" %(data['group'],data['login']))
                if int(obj['code']) != 0:
                    dataerreur['data']['msg'] = "%s attribution compte %s"%(dataerreur['data']['msg'],obj['result'])
                    warning = true
                if warning:
                    raise
            else:
                dataerreur['data']['msg'] = "ERROR : createuser pas pris encore en compte sur mac OS"   
                dataerreur['ret']=255
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
