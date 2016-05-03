# -*- coding: utf-8 -*-
import json
from lib.networkinfo import interfacename, rewriteInterfaceTypeRedhad, rewriteInterfaceTypeDebian, getWindowsNameInterfaceForMacadress

from lib.utils import  simplecommandestr, simplecommande
import sys, os, platform
from  lib.utils import pulginprocess

plugin={"VERSION": "1.0", "NAME" :"updateipinfo"}

@pulginprocess
def action( objetxmpp, action, sessionid, data, message, dataerreur,result):
    if sys.platform.startswith('linux'):
        interface = interfacename(data['mac'])
        if interface == "":
            dataerreur['data']['msg'] = "ERROR : updateipinfo :[Pas reusi a determiner nom interface a modifier]"
            raise
        if os.path.isfile("/etc/NetworkManager/NetworkManager.conf"):
            dataerreur['data']['msg'] = "ERROR : updateipinfo :[Ce n'est pas un server utilisation Network-Manager]"
            raise
        
        if typelinuxfamily() == 'debian':
            if not rewriteInterfaceTypeDebian(data,interface):
                dataerreur['data']['msg'] = "ERROR : updateipinfo :[debian type erreur reecriture fichier interfaces]"
                raise
        else:
            if os.path.isdir("/etc/sysconfig/network-scripts"):
                obj = simplecommande("ls *%s"%interface)
                if len(obj['result']) == 1 :                            
                    interfacefile = "/etc/sysconfig/network-scripts/%s"%obj['result']
                    if not rewriteInterfaceTypeRedhad(interfacefile, data, interface):
                        dataerreur['data']['msg'] = "ERROR : updateipinfo :[redhat type erreur reecriture fichier in /etc/sysconfig/network-scripts]"
                    raise
    elif sys.platform.startswith('win'):
        name_interface = getWindowsNameInterfaceForMacadress(data['mac'])
        if data['dhcp'] == True:
            obj = simplecommande("netsh interface ip set address \"%s\" dhcp"%name_interface)
            
        else:
            obj = simplecommande("netsh interface ip set address %s static %s %s"%(name_interface,data['ipaddress'],data['mask']))
    else:
        #mac os a completer
        dataerreur['data']['msg'] = "ERROR : updateipinfo pas pris encore en compte"   
        dataerreur['ret']=255
        raise 
    