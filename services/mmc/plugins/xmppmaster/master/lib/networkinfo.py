#!/usr/bin/env python
# -*- coding: utf-8 -*-

import netifaces
import json
import subprocess
import sys
import platform
import utils

if sys.platform.startswith('win'):
    import wmi
    import pythoncom

class  networkagentinfo:
    def __init__(self, sessionid, action ='resultgetinfo',param=[]):
        self.sessionid = sessionid
        self.action = action
        self.messagejson = {}
        self.networkobjet(self.sessionid, self.action)
        #print self.messagejson['listipinfo']
        for d in self.messagejson['listipinfo']:            
            d['macnonreduite']=d['macaddress']
            d['macaddress'] = self.reduction_mac(d['macaddress'])
        #print self.messagejson['listipinfo'] 
        if len(param) != 0 and len(self.messagejson['listipinfo']) != 0:
            #filtre resultat
            dd=[]
            param1 = map(self.reduction_mac,param)
            for d in self.messagejson['listipinfo']:
                e=[s for s in param1 if d['macaddress'] == s]
                if len(e)!=0:
                    dd.append(d)
            self.messagejson['listipinfo']=dd
    #self.NetWorkInfo = json.dumps(self.networkobjet("desder"), indent=4, sort_keys=True)
    def reduction_mac(self, mac):
        mac=mac.lower()
        mac = mac.replace(":","")
        mac = mac.replace("-","")
        mac = mac.replace(" ","")
        #mac = mac.replace("/","")
        return mac

    def networkobjet(self, sessionid, action):
        self.messagejson={}
        self.messagejson['action']     = action
        self.messagejson['sessionid']  = sessionid
        self.messagejson['listdns']    = []
        self.messagejson['listipinfo'] = []
        self.messagejson['dhcp']       = 'False'
        self.messagejson['dnshostname']= ''
        self.messagejson['msg']        = platform.system()
        if sys.platform.startswith('linux'):
                # Linux-specific code here...
                p = subprocess.Popen("ps aux | grep dhclient | grep -v leases | grep -v grep | awk '{print $NF}'",
                                                    shell=True, 
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.STDOUT)
                result = p.stdout.readlines()
                code_result= p.wait()
                if len(result) > 0:
                    self.messagejson['dhcp']   = 'True'
                else:
                    self.messagejson['dhcp']   = 'False'
                
                self.messagejson['listdns']    = self.listdnslinux()
                self.messagejson['listipinfo'] = self.getLocalIipAddress()
                self.messagejson['dnshostname']= platform.node()
                return self.messagejson

        elif sys.platform.startswith('win'):
            ##code windows
            #import wmi
            """ revoit objet reseau windows """
            pythoncom.CoInitialize ()
            try:
                wmi_obj = wmi.WMI()
                wmi_sql = "select * from Win32_NetworkAdapterConfiguration where IPEnabled=TRUE"
                wmi_out = wmi_obj.query( wmi_sql )
            finally:
                pythoncom.CoUninitialize ()
            for dev in wmi_out:
                objnet={}
                objnet['macaddress'] = dev.MACAddress
                objnet['ipaddress']  = dev.IPAddress[0]
                try:
                    objnet['gateway']    = dev.DefaultIPGateway[0]
                except:
                    objnet['gateway']    = ""
                objnet['mask']       = dev.IPSubnet[0]
                objnet['dhcp']       = dev.DHCPEnabled
                objnet['dhcpserver'] = dev.DHCPServer
                objnet['brodcast'] = ''
                self.messagejson['listipinfo'].append(objnet)
                try:
                    self.messagejson['listdns'].append( dev.DNSServerSearchOrder[0] )
                except:
                    pass
                self.messagejson['dnshostname']      = dev.DNSHostName
            self.messagejson['msg']     = platform.system()    
            return self.messagejson

        elif sys.platform.startswith('darwin'):
            #code pour MacOs
            return self.MacOsNetworkInfo()
        else:           
            self.messagejson['msg']= "system %s : pas encore pris en compte"%sys.platform
            return self.messagejson

    def routeinterface(self):
        """renvoi la liste des ip gateway en fonction de l'interface linux"""
        p = subprocess.Popen('LANG=C route -n | grep \'UG[ \t]\' | awk \'{ print $8"="$2}\'',
                                                shell=True, 
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT)
        result = p.stdout.readlines()
        code_result= p.wait()
        dataroute=[]
        obj1={}
        for i in range(len(result)):
            #print result[i].rstrip('\n')
            result[i]=result[i].rstrip('\n')    
            d = result[i].split("=")
            obj1[d[0]]=d[1]
        return obj1

    def validIP(self, address):
        parts = address.split(".")
        if len(parts) != 4:
            return False
        for item in parts:
            if not 0 <= int(item) <= 255:
                return False
        return True

    def IpDhcp(self):
        obj1={}
        system=""
        ipdhcp = ""
        ipadress = ""
        p = subprocess.Popen('cat /proc/1/comm',
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        result = p.stdout.readlines()
        code_result= p.wait()
        system=result[0].rstrip('\n')    
        """renvoi la liste des ip gateway en fonction de l'interface linux"""
    
        if system == "init":
            p = subprocess.Popen('cat /var/log/syslog | grep -e DHCPACK | tail -n10 | awk \'{print $(NF-2)"@" $NF}\'',
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            result = p.stdout.readlines()
            code_result= p.wait()
            
            for i in range(len(result)):
                result[i]=result[i].rstrip('\n')    
                d = result[i].split("@")
                obj1[d[0]]=d[1]
        elif system == "systemd":
            #p = subprocess.Popen('systemctl status network | grep -i "dhclient\["',
            p = subprocess.Popen('journalctl | grep "dhclient\["',
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            result = p.stdout.readlines()
            code_result= p.wait()
            for i in result:
                i = i.rstrip('\n')
                colonne=i.split(" ")
                if "DHCPACK" in i:
                    ipdhcp = ""
                    ipadress = ""
                    ipdhcp = colonne[-1:][0]
                elif "bound to" in i:
                    for z in colonne:                    
                        if self.validIP(z):
                            ipadress = z
                            if  ipdhcp != "":
                                obj1[ipadress] = ipdhcp
                            break
                    ipdhcp = ""
                    ipadress = ""    
                else:
                    continue
        return obj1

    def MacAdressToIp(self, ip):
        'Returns a list of MACs for interfaces that have given IP, returns None if not found'
        for i in netifaces.interfaces():
            addrs = netifaces.ifaddresses(i)
            try:
                if_mac = addrs[netifaces.AF_LINK][0]['addr']
                if_ip = addrs[netifaces.AF_INET][0]['addr']
            except:# IndexError, KeyError: #ignore ifaces that dont have MAC or IP
                if_mac = if_ip = None
            if if_ip == ip:
                return if_mac
        return None

    def MacOsNetworkInfo(self):
        self.messagejson={}
        self.messagejson["dnshostname"] =  platform.node()
        self.messagejson["listipinfo"]=[]
        self.messagejson["dhcp"] = 'False'
        for i in netifaces.interfaces():
            addrs = netifaces.ifaddresses(i)
            try:
                if_mac = addrs[netifaces.AF_LINK][0]['addr']
                if_ip = addrs[netifaces.AF_INET][0]['addr']
                p = subprocess.Popen('ipconfig getpacket %s'%i,
                                        shell=True, 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                result = p.stdout.readlines()
                code_result= p.wait()
                if code_result == 0 :
                    #print if_mac
                    #print if_ip
                    partinfo={}
                    partinfo["dhcpserver"] = ''
                    partinfo["dhcp"] = 'False'
                    partinfo["brodcast"] = ''
                    for i in result:
                        i = i.rstrip('\n')
                        colonne = i.split("=")
                        if len(colonne) != 2:
                            colonne = i.split(":")                    
                        if colonne[0].strip().startswith('yiaddr'):
                            #yiaddr = 192.168.0.12
                            partinfo["ipaddress"] = colonne[1].strip()
                        elif colonne[0].strip().startswith('chaddr'):
                            #chaddr = 0:88:65:35:32:f0
                            partinfo["macaddress"] = colonne[1].strip()
                        elif colonne[0].strip().startswith('subnet_mask'):
                            #subnet_mask (ip): 255.255.255.0
                            partinfo["mask"] = colonne[1].strip()                        
                        elif colonne[0].strip().startswith('router'):
                            #router (ip_mult): {192.168.0.1}
                            partinfo["gateway"] = colonne[1].strip(" {}")
                        elif colonne[0].strip().startswith('server_identifier'):
                            #server_identifier (ip): 192.168.0.1
                            partinfo["dhcpserver"] = colonne[1].strip()
                            partinfo["dhcp"] = 'True'
                            self.messagejson["dhcp"] = 'True'
                        elif colonne[0].strip().startswith('domain_name_server'):
                            #domain_name_server (ip_mult): {8.8.8.8, 0.0.0.0}
                            self.messagejson["listdns"] = colonne[1].strip(" {}").split(",")
                            self.messagejson["listdns"] = [x.strip() for x in self.messagejson["listdns"]]
                        else:
                            continue
                    try:
                        if partinfo["ipaddress"] != '':
                            self.messagejson["listipinfo"].append(partinfo)
                    except:
                        pass
            except:# IndexError, KeyError: #ignore ifaces that dont have MAC or IP
                pass
        return self.messagejson   

    ###linux
    def getLocalIipAddress(self):
        #renvoi objet reseaux linux.
        dataroute = self.routeinterface()
        dhcpserver = self.IpDhcp()
        ip_addresses = []
        interfaces = netifaces.interfaces()
        for i in interfaces:       
            if i == 'lo': continue
            iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
            if iface:
                for j in iface:
                    if j['addr'] != '127.0.0.1' and self.MacAdressToIp(j['addr']) != None:
                        obj={}
                        obj['ipaddress'] = j['addr']
                        obj['mask']   = j['netmask']
                        try : 
                            obj['broadcast']   = j['broadcast']
                        except:
                            obj['broadcast']   = "0.0.0.0"
                        try:
                            if dataroute[str(i)] != None:                       
                                obj['gateway'] = dataroute[str(i)]
                            else:
                                obj['gateway'] = "0.0.0.0"
                        except:
                            obj['gateway'] = "0.0.0.0"

                        obj['macaddress'] = self.MacAdressToIp(j['addr'])
                        try:
                            if dhcpserver[j['addr']] != None:
                                obj['dhcp'] = 'True'
                                obj['dhcpserver'] = dhcpserver[j['addr']]    
                            else:
                                obj['dhcp'] = 'False'
                                obj['dhcpserver'] = "0.0.0.0" 
                        except:
                            obj['dhcp'] = 'False'
                            obj['dhcpserver'] = "0.0.0.0"         
                        ip_addresses.append(obj)
        return ip_addresses

    def listdnslinux(self):
        dns=[]
        p = subprocess.Popen("cat /etc/resolv.conf | grep nameserver | awk '{print $2}'",
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        result = p.stdout.readlines()
        code_result= p.wait()
        for i in result:
            #i = i.rstrip('\n')
            dns.append(i.rstrip('\n'))
        return dns

    ##print json.dumps(networkobjet("desder"), indent=4, sort_keys=True)

#er=networkagent("ddd","ddddd",["e0:06:e6:c7:9b:7f","d6:45:49:94:74:b0"])
##er=networkagent("ddd","ddddd")
#print json.dumps(er.messagejson, indent=4, sort_keys=True)
###
"""
cads ubuntu
l’activation par défaut du paquet resolvconf. Ce paquet permet de gérer le contenu du fichier resolv.conf de façon plus précise. Tout ce passe dans le dossier /etc/resolvconf/resolv.conf.d/. Il contient trois fichiers : base, head, original, qui ont chacun un rôle plus ou moins important dans le contenu du resolv.conf.

"""
###
class updatedns:
    def __init__(self, sessionid, action ='resultupdatednsinfo',param=[]):
        self.sessionid = sessionid
        self.action = action
        self.messagejson = {}
        self.messagejson['sessionid']=sessionid
        self.messagejson['ret']=0
        self.messagejson['base64']=False
        self.messagejson['data']={}
        if len(param) == 0 :
            self.messagejson['ret']=255
            self.messagejson['data']['msg']="Error: list dns vide"
            return
        if sys.platform.startswith('linux'):
            mon_fichier = open("/etc/resolv.conf", "wb")
            for t in param:
                #if is_valid_ipv4(param):
                mon_fichier.write("nameserver\t%s"%param)
            print windowsservice('networking','restart')  
        elif sys.platform.startswith('win'):
            
            pass
        elif sys.platform.startswith('darwin'):
            pass
        else:
            self.messagejson['data']['msg']="Error: commande sur Osnon pris en compte"
            self.messagejson['ret']=254
        
##netinfo = networkagentinfo("25", resultaction, strip_list)
def interfacename(mac):  
    for i in netifaces.interfaces():
        if isInterfaceToMacadress(i,mac):
            return i
    return ""    


def lit_networkconf():
    pass


def isInterfaceToMacadress(interface, mac):
    addrs = netifaces.ifaddresses(interface)
    try:
        if_mac = addrs[netifaces.AF_LINK][0]['addr']
    except:# IndexError, KeyError: #ignore ifaces that dont have MAC or IP
        return False
    if if_mac == mac:
        return True
    return False


def isInterfaceToIpadress(interface, ip):
    addrs = netifaces.ifaddresses(interface)
    try:
        if_ip = addrs[netifaces.AF_INET][0]['addr']
    except:# IndexError, KeyError: #ignore ifaces that dont have MAC or IP
        return False
    if if_ip == ip:
        return True
    return False


def rewriteInterfaceTypeRedhad(file, data,interface):
    tab=[]
    inputFile = open(file, 'rb')
    contenue = inputFile.read()
    inputFile.close()
    tab = contenue.split("\n")
    ll=  [ x   for x in tab if \
        not x.strip().startswith('IPADDR')\
        and not x.strip().startswith('NETMASK')\
        and not x.strip().startswith('NETWORK')\
        and not x.strip().startswith('GATEWAY')\
        and not x.strip().startswith('BROADCAST')\
        and not x.strip().startswith('BOOTPROTO')]
    try:
        if data['dhcp']:
            ll.insert(1, "BOOTPROTO=dhcp")
        else:
            ll.insert(1, 'BOOTPROTO=static')
            ll.append("IPADDR=%s"%data['ipaddress'])
            ll.append("NETMASK=%s"%data['mask'])
            ll.append("GATEWAY=%s"%data['gateway'])
        strr="\n".join(ll)    
        inputFile = open(file, 'wb')
        inputFile.write(strr)
        inputFile.close()    
    except:
        return False
    return True


def rewriteInterfaceTypeDebian(data,interface ):
    tab=[]
    z=[]
    try:
        inputFile = open("/etc/network/interfaces", 'rb')
        contenue = inputFile.read()
        inputFile.close()
        #sauve fichier de conf
        inputFile = open("/etc/network/interfacesold", 'wb')
        inputFile.write(contenue)
        inputFile.close()
        b = contenue.split("\n")
        ll=[x.strip() for x in b if not x.startswith('auto') and\
            not 'auto' in x and not x.startswith('#') and x !='']
        string="\n".join(ll)
        ll=[x.strip() for x in string.split('iface') if x!='']
        for t in ll:
            if t.split(" ")[0] != interface:
                z.append(t)
        if data['dhcp'] == True:
            tab.append("\nauto %s\n"%interface )
            tab.append("iface %s inet dhcp\n"%interface)
        else:
            tab.append("auto %s\n"%interface )
            tab.append("iface %s inet static\n"%interface)
            tab.append("\taddress %s\n"%data['ipaddress'])
            tab.append("\tnetmask %s\n"%data['mask'])
            tab.append("\tgateway %s\n"%data['gateway'])
        val1="".join(tab)
        for t in z:
            val = "\nauto %s\niface "%t.split(" ")[0]
            val ="%s %s\n"%(val,t)
        inputFile = open("/etc/network/interfaces", 'wb')
        inputFile.write("%s\n%s"%(val,val1))
        inputFile.close()
        return True
    except:
        return False

def typelinuxfamily():
    debiandist = ['astra', 'canaima', 'collax', 'cumulus', 'damn', 'debian', 'doudoulinux', 'euronode', 'finnix', 'grml', 'kanotix', 'knoppix', 'linex', 'linspire',   'advanced', 'lmde', 'mepis','ocera', 'ordissimo','parsix', 'pureos', 'rays', 'aptosid', 'ubuntu', 'univention', 'xandros']
    redhadlist=['centos', 'rhel', 'redhat', 'fedora', 'mageia','mga', 'mandiva', 'suse', 'oracle', 'scientific', 'fermi']
    val = platform.platform().lower()
    for t in debiandist:
        if t in val:
            return 'debian'
    return 'redhat'
 
def getsystemressource():
    p = subprocess.Popen('cat /proc/1/comm',
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    code_result= p.wait()
    system=result[0].rstrip('\n')
    return system

def getWindowsNameInterfaceForMacadress(macadress):
    obj = utils.simplecommande("wmic NIC get MACAddress,NetConnectionID")
    for lig in obj['result']:
        l = lig.lower()
        mac = macadress.lower()
        if l.startswith(mac):                
            element=lig.split(' ')
            element[0]=''
            fin = [x for x in element if x.strip()!=""]
            return  " ".join(fin)
                
