# -*- coding: utf-8 -*-
import json, os
from lib.networkinfo import interfacename, rewriteInterfaceTypeRedhad, rewriteInterfaceTypeDebian, getWindowsNameInterfaceForMacadress

from lib.utils import  simplecommandestr, simplecommande
import sys, os, platform
from  lib.utils import pulginprocess, pathscriptperl

plugin={"VERSION": "1.0", "NAME" :"updateipinfoperl"}

@pulginprocess
def action( objetxmpp, action, sessionid, data, message, dataerreur, result):
    if sys.platform.startswith('linux'):
        interface = interfacename(data['mac'])
        if interface == "":
            dataerreur['data']['msg'] = "ERROR : updateipinfo :[Pas reusi a determiner nom interface a modifier]"
            raise
        if os.path.isfile("/etc/NetworkManager/NetworkManager.conf"):
            dataerreur['data']['msg'] = "ERROR : updateipinfo :[Ce n'est pas un server utilisation Network-Manager]"
            raise

        if data['dhcp'] == True:
            option_dhcp="-d0 -m%s"%(data['mac'])
        else:
            option_dhcp="-d1 -m%s -i%s -n%s -g%s"%(data['mac'],data['ipaddress'],data['mask'],data['gateway'])
        if typelinuxfamily() == 'debian':
            optionarg="perl %s -h1 %s"%(pathscriptperl("reconfigurationVM.pl"),option_dhcp)            
        else:
            optionarg="perl %s -h0 %s"%(pathscriptperl("reconfigurationVM.pl"),option_dhcp)
        obj = simplecommandestr(optionarg)
        if obj['code'] != 0:
            dataerreur['data']['msg'] = "ERROR : updateipinfo :[%s]"%obj['result']
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
    