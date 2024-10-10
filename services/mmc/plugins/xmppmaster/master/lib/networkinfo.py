#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# FILE : pulse_xmpp_agent/lib/networkinfo.py

import netifaces
import subprocess
import sys
import platform
from . import utils
import socket
import psutil

import ipaddress

if sys.platform.startswith("win"):
    import wmi
    import pythoncom


def find_common_addresses(list1, list2):
    """
    Trouve les adresses IP communes entre deux listes de réseaux CIDR.

    Cette fonction prend deux listes de chaînes de caractères représentant des réseaux CIDR,
    les convertit en objets IPv4Network, et recherche les adresses IP communes dans les deux listes.

    Args:
        list1 (list of str): Une liste de chaînes de caractères représentant des réseaux CIDR.
        list2 (list of str): Une autre liste de chaînes de caractères représentant des réseaux CIDR.

    Returns:
        list of str: Une liste d'adresses IP communes entre les deux listes de réseaux CIDR.
    """
    # Convertir les chaînes de CIDR en objets IPv4Network
    cidr_list1 = [ipaddress.ip_network(cidr) for cidr in list1]
    cidr_list2 = [ipaddress.ip_network(cidr) for cidr in list2]

    # Chercher des adresses IP communes dans les deux listes
    common_addresses = []
    for net1 in cidr_list1:
        for net2 in cidr_list2:
            # Vérifier si les réseaux se chevauchent
            if net1.overlaps(net2):
                # Ajouter l'IP commune à la liste
                common_addresses.append(str(net1.network_address))

    return common_addresses

def get_CIDR_ipv4_addresses(exclude_localhost=True):
    """
    Récupère les adresses IPv4 au format CIDR pour chaque interface réseau de la machine.

    Cette fonction utilise des commandes spécifiques au système d'exploitation pour obtenir les informations
    sur les interfaces réseau et les adresses IPv4. Elle retourne une liste d'adresses IPv4 au format CIDR.

    Args:
        exclude_localhost (bool): Si True, exclut les interfaces locales (localhost ou 127.0.0.1).

    Returns:
        list: Une liste d'adresses IPv4 au format CIDR (par exemple, '192.168.1.0/24').
    """
    ipv4_addresses = []
    # Vérifier le système d'exploitation
    system = platform.system()
    if system == "Windows":
        # Commande pour obtenir les interfaces réseau sous Windows
        output = subprocess.check_output("ipconfig", shell=True).decode()
        ip, mask = None, None
        for line in output.splitlines():
            if "IPv4 Address" in line or "IPv4" in line:
                ip = line.split(":")[-1].strip()
            if "Subnet Mask" in line:
                mask = line.split(":")[-1].strip()
                if ip and mask:
                    if exclude_localhost and ip == "127.0.0.1":
                        continue
                    cidr = ipaddress.IPv4Network(f'{ip}/{mask}', strict=False).with_prefixlen
                    ipv4_addresses.append(cidr)
                    ip, mask = None, None
    elif system == "Linux":
        # Commande pour obtenir les interfaces réseau sous Linux
        output = subprocess.check_output("ip addr show", shell=True).decode()
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                parts = line.split()
                ip_mask = parts[1]  # Exemple : 192.168.1.100/24
                if exclude_localhost and ip_mask.startswith("127.0.0.1/"):
                    continue
                ipv4_addresses.append(ip_mask)
    elif system == "Darwin":  # macOS est identifié par 'Darwin'
        # Commande pour obtenir les interfaces réseau sous macOS
        output = subprocess.check_output("ifconfig", shell=True).decode()
        current_ip = None
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("inet ") and "127.0.0.1" not in line:  # Éviter localhost
                parts = line.split()
                ip = parts[1]  # L'adresse IP est le second champ
                mask = parts[3]  # Le masque est généralement le quatrième champ
                if exclude_localhost and ip == "127.0.0.1":
                    continue
                cidr = ipaddress.IPv4Network(f'{ip}/{mask}', strict=False).with_prefixlen
                ipv4_addresses.append(cidr)
    return ipv4_addresses

class networkagentinfo:
    def __init__(self, sessionid, action="resultgetinfo", param=[]):
        self.sessionid = sessionid
        self.action = action
        self.messagejson = {}
        self.networkobjet(self.sessionid, self.action)
        for d in self.messagejson["listipinfo"]:
            d["macnotshortened"] = d["macaddress"]
            d["macaddress"] = self.reduction_mac(d["macaddress"])
        if len(param) != 0 and len(self.messagejson["listipinfo"]) != 0:
            # Filter result
            dd = []
            param1 = list(map(self.reduction_mac, param))
            for d in self.messagejson["listipinfo"]:
                e = [s for s in param1 if d["macaddress"] == s]
                if len(e) != 0:
                    dd.append(d)
            self.messagejson["listipinfo"] = dd

    def reduction_mac(self, mac):
        mac = mac.lower()
        mac = mac.replace(":", "")
        mac = mac.replace("-", "")
        mac = mac.replace(" ", "")
        # mac = mac.replace("/","")
        return mac

    def getuser(self):
        userlist = list({users[0] for users in psutil.users()})
        return userlist

    def networkobjet(self, sessionid, action):
        self.messagejson["action"] = action
        self.messagejson["sessionid"] = sessionid
        self.messagejson["listdns"] = []
        self.messagejson["listipinfo"] = []
        self.messagejson["dhcp"] = "False"
        self.messagejson["dnshostname"] = ""
        self.messagejson["msg"] = platform.system()
        try:
            self.messagejson["users"] = self.getuser()
        except:
            self.messagejson["users"] = ["system"]

        if sys.platform.startswith("linux"):
            # Linux-specific code here...
            p = subprocess.Popen(
                "ps aux | grep dhclient | grep -v leases | grep -v grep | awk '{print $NF}'",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            result = p.stdout.readlines()
            code_result = p.wait()
            if len(result) > 0:
                self.messagejson["dhcp"] = "True"
            else:
                self.messagejson["dhcp"] = "False"
            self.messagejson["listdns"] = self.listdnslinux()
            self.messagejson["listipinfo"] = self.getLocalIipAddress()
            self.messagejson["dnshostname"] = platform.node()
            return self.messagejson

        elif sys.platform.startswith("win"):
            # code windows
            # import wmi
            """revoit objet reseau windows"""
            pythoncom.CoInitialize()
            try:
                wmi_obj = wmi.WMI()
                wmi_sql = "select * from Win32_NetworkAdapterConfiguration where IPEnabled=TRUE"
                wmi_out = wmi_obj.query(wmi_sql)
            finally:
                pythoncom.CoUninitialize()
            for dev in wmi_out:
                objnet = {}
                objnet["macaddress"] = dev.MACAddress
                objnet["ipaddress"] = dev.IPAddress[0]
                try:
                    objnet["gateway"] = dev.DefaultIPGateway[0]
                except:
                    objnet["gateway"] = ""
                objnet["mask"] = dev.IPSubnet[0]
                objnet["dhcp"] = dev.DHCPEnabled
                objnet["dhcpserver"] = dev.DHCPServer
                self.messagejson["listipinfo"].append(objnet)
                try:
                    self.messagejson["listdns"].append(dev.DNSServerSearchOrder[0])
                except:
                    pass
                self.messagejson["dnshostname"] = dev.DNSHostName
            self.messagejson["msg"] = platform.system()
            return self.messagejson

        elif sys.platform.startswith("darwin"):
            # code pour MacOs
            return self.MacOsNetworkInfo()
        else:
            self.messagejson["msg"] = "system %s : not managed yet" % sys.platform
            return self.messagejson

    def isIPValid(self, ipaddress):
        """
        This function tests the provided IP Address to see
        if it is a valid IP or not.
        Only IPv4 is supported.

        @param ipaddress: The ip address to test

        @rtype: Boolean. True if the ip adress is valid, False otherwise
        """
        try:
            socket.inet_aton(ipaddress)
            return True
        except socket.error:
            return False

    def IpDhcp(self):
        obj1 = {}
        system = ""
        ipdhcp = ""
        ipadress = ""
        p = subprocess.Popen(
            "cat /proc/1/comm",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        result = p.stdout.readlines()
        code_result = p.wait()
        system = result[0].rstrip("\n")
        """ Returns the list of ip gateways for linux interfaces """

        if system == "init":
            p = subprocess.Popen(
                "cat /var/log/syslog | grep -e DHCPACK | tail -n10 | awk '{print $(NF-2)\"@\" $NF}'",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            result = p.stdout.readlines()
            code_result = p.wait()

            for i in range(len(result)):
                result[i] = result[i].rstrip("\n")
                d = result[i].split("@")
                obj1[d[0]] = d[1]
        elif system == "systemd":
            # p = subprocess.Popen('systemctl status network | grep -i "dhclient\["',
            p = subprocess.Popen(
                'journalctl | grep "dhclient["',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            result = p.stdout.readlines()
            code_result = p.wait()
            for i in result:
                i = i.rstrip("\n")
                colonne = i.split(" ")
                if "DHCPACK" in i:
                    ipdhcp = ""
                    ipadress = ""
                    ipdhcp = colonne[-1:][0]
                elif "bound to" in i:
                    for z in colonne:
                        if self.isIPValid(z):
                            ipadress = z
                            if ipdhcp != "":
                                obj1[ipadress] = ipdhcp
                            break
                    ipdhcp = ""
                    ipadress = ""
                else:
                    continue
        return obj1

    def MacAdressToIp(self, ip):
        "Returns a list of MACs for interfaces that have given IP, returns None if not found"
        for i in netifaces.interfaces():
            addrs = netifaces.ifaddresses(i)
            try:
                if_mac = addrs[netifaces.AF_LINK][0]["addr"]
                if_ip = addrs[netifaces.AF_INET][0]["addr"]
            except:  # IndexError, KeyError: #ignore ifaces that dont have MAC or IP
                if_mac = if_ip = None
            if if_ip == ip:
                return if_mac
        return None

    def MacOsNetworkInfo(self):
        self.messagejson = {}
        self.messagejson["dnshostname"] = platform.node()
        self.messagejson["listipinfo"] = []
        self.messagejson["dhcp"] = "False"
        for i in netifaces.interfaces():
            addrs = netifaces.ifaddresses(i)
            try:
                if_mac = addrs[netifaces.AF_LINK][0]["addr"]
                if_ip = addrs[netifaces.AF_INET][0]["addr"]
                p = subprocess.Popen(
                    "ipconfig getpacket %s" % i,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                result = p.stdout.readlines()
                code_result = p.wait()
                if code_result == 0:
                    # print if_mac
                    # print if_ip
                    partinfo = {}
                    partinfo["dhcpserver"] = ""
                    partinfo["dhcp"] = "False"
                    for i in result:
                        i = i.rstrip("\n")
                        colonne = i.split("=")
                        if len(colonne) != 2:
                            colonne = i.split(":")
                        if colonne[0].strip().startswith("yiaddr"):
                            # yiaddr = 192.168.0.12
                            partinfo["ipaddress"] = colonne[1].strip()
                        elif colonne[0].strip().startswith("chaddr"):
                            # chaddr = 0:88:65:35:32:f0
                            partinfo["macaddress"] = colonne[1].strip()
                        elif colonne[0].strip().startswith("subnet_mask"):
                            # subnet_mask (ip): 255.255.255.0
                            partinfo["mask"] = colonne[1].strip()
                        elif colonne[0].strip().startswith("router"):
                            # router (ip_mult): {192.168.0.1}
                            partinfo["gateway"] = colonne[1].strip(" {}")
                        elif colonne[0].strip().startswith("server_identifier"):
                            # server_identifier (ip): 192.168.0.1
                            partinfo["dhcpserver"] = colonne[1].strip()
                            partinfo["dhcp"] = "True"
                            self.messagejson["dhcp"] = "True"
                        elif colonne[0].strip().startswith("domain_name_server"):
                            # domain_name_server (ip_mult): {8.8.8.8, 0.0.0.0}
                            self.messagejson["listdns"] = (
                                colonne[1].strip(" {}").split(",")
                            )
                            self.messagejson["listdns"] = [
                                x.strip() for x in self.messagejson["listdns"]
                            ]
                        else:
                            continue
                    try:
                        if partinfo["ipaddress"] != "":
                            self.messagejson["listipinfo"].append(partinfo)
                    except:
                        pass
            except:  # IndexError, KeyError: #ignore ifaces that dont have MAC or IP
                pass
        return self.messagejson

    def getLocalIipAddress(self):
        # renvoi objet reseaux linux.
        dhcpserver = self.IpDhcp()
        ip_addresses = []
        defaultgateway = {}
        try:
            gws = netifaces.gateways()
            intergw = gws["default"][netifaces.AF_INET]
            defaultgateway[intergw[1]] = intergw[0]
        except Exception:
            pass
        interfaces = netifaces.interfaces()
        for i in interfaces:
            if i == "lo":
                continue
            iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
            if iface:
                for j in iface:
                    if (
                        j["addr"] != "127.0.0.1"
                        and self.MacAdressToIp(j["addr"]) != None
                    ):
                        obj = {}
                        obj["ipaddress"] = j["addr"]
                        obj["mask"] = j["netmask"]
                        try:
                            obj["broadcast"] = j["broadcast"]
                        except:
                            obj["broadcast"] = "0.0.0.0"
                        try:
                            if str(i) in defaultgateway:
                                obj["gateway"] = defaultgateway[str(i)]
                            else:
                                obj["gateway"] = "0.0.0.0"
                        except Exception:
                            obj["gateway"] = "0.0.0.0"

                        obj["macaddress"] = self.MacAdressToIp(j["addr"])
                        try:
                            if dhcpserver[j["addr"]] != None:
                                obj["dhcp"] = "True"
                                obj["dhcpserver"] = dhcpserver[j["addr"]]
                            else:
                                obj["dhcp"] = "False"
                                obj["dhcpserver"] = "0.0.0.0"
                        except:
                            obj["dhcp"] = "False"
                            obj["dhcpserver"] = "0.0.0.0"
                        ip_addresses.append(obj)
        return ip_addresses

    def listdnslinux(self):
        dns = []
        p = subprocess.Popen(
            "cat /etc/resolv.conf | grep nameserver | awk '{print $2}'",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        result = p.stdout.readlines()
        code_result = p.wait()
        for i in result:
            # i = i.rstrip('\n')
            dns.append(i.rstrip("\n"))
        return dns


def interfacename(mac):
    for i in netifaces.interfaces():
        if isInterfaceToMacadress(i, mac):
            return i
    return ""


def lit_networkconf():
    pass


def isInterfaceToMacadress(interface, mac):
    addrs = netifaces.ifaddresses(interface)
    try:
        if_mac = addrs[netifaces.AF_LINK][0]["addr"]
    except:  # IndexError, KeyError: #ignore ifaces that dont have MAC or IP
        return False
    if if_mac == mac:
        return True
    return False


def isInterfaceToIpadress(interface, ip):
    addrs = netifaces.ifaddresses(interface)
    try:
        if_ip = addrs[netifaces.AF_INET][0]["addr"]
    except:  # IndexError, KeyError: #ignore ifaces that dont have MAC or IP
        return False
    if if_ip == ip:
        return True
    return False


def rewriteInterfaceTypeRedhad(file, data, interface):
    tab = []
    inputFile = open(file, "rb")
    contenue = inputFile.read()
    inputFile.close()
    tab = contenue.split("\n")
    ll = [
        x
        for x in tab
        if not x.strip().startswith("IPADDR")
        and not x.strip().startswith("NETMASK")
        and not x.strip().startswith("NETWORK")
        and not x.strip().startswith("GATEWAY")
        and not x.strip().startswith("BROADCAST")
        and not x.strip().startswith("BOOTPROTO")
    ]
    try:
        if data["dhcp"]:
            ll.insert(1, "BOOTPROTO=dhcp")
        else:
            ll.insert(1, "BOOTPROTO=static")
            ll.append("IPADDR=%s" % data["ipaddress"])
            ll.append("NETMASK=%s" % data["mask"])
            ll.append("GATEWAY=%s" % data["gateway"])
        strr = "\n".join(ll)
        inputFile = open(file, "wb")
        inputFile.write(strr)
        inputFile.close()
    except:
        return False
    return True


def rewriteInterfaceTypeDebian(data, interface):
    tab = []
    z = []
    try:
        inputFile = open("/etc/network/interfaces", "rb")
        contenue = inputFile.read()
        inputFile.close()
        # sauve fichier de conf
        inputFile = open("/etc/network/interfacesold", "wb")
        inputFile.write(contenue)
        inputFile.close()
        b = contenue.split("\n")
        ll = [
            x.strip()
            for x in b
            if not x.startswith("auto")
            and not "auto" in x
            and not x.startswith("#")
            and x != ""
        ]
        string = "\n".join(ll)
        ll = [x.strip() for x in string.split("iface") if x != ""]
        for t in ll:
            if t.split(" ")[0] != interface:
                z.append(t)
        if data["dhcp"] == True:
            tab.append("\nauto %s\n" % interface)
            tab.append("iface %s inet dhcp\n" % interface)
        else:
            tab.append("auto %s\n" % interface)
            tab.append("iface %s inet static\n" % interface)
            tab.append("\taddress %s\n" % data["ipaddress"])
            tab.append("\tnetmask %s\n" % data["mask"])
            tab.append("\tgateway %s\n" % data["gateway"])
        val1 = "".join(tab)
        for t in z:
            val = "\nauto %s\niface " % t.split(" ")[0]
            val = "%s %s\n" % (val, t)
        inputFile = open("/etc/network/interfaces", "wb")
        inputFile.write("%s\n%s" % (val, val1))
        inputFile.close()
        return True
    except:
        return False


def typelinuxfamily():
    debiandist = [
        "astra",
        "canaima",
        "collax",
        "cumulus",
        "damn",
        "debian",
        "doudoulinux",
        "euronode",
        "finnix",
        "grml",
        "kanotix",
        "knoppix",
        "linex",
        "linspire",
        "advanced",
        "lmde",
        "mepis",
        "ocera",
        "ordissimo",
        "parsix",
        "pureos",
        "rays",
        "aptosid",
        "ubuntu",
        "univention",
        "xandros",
    ]
    redhadlist = [
        "centos",
        "rhel",
        "redhat",
        "fedora",
        "mageia",
        "mga",
        "mandriva",
        "suse",
        "oracle",
        "scientific",
        "fermi",
    ]
    val = platform.platform().lower()
    for t in debiandist:
        if t in val:
            return "debian"
    return "redhat"


def getsystemressource():
    p = subprocess.Popen(
        "cat /proc/1/comm", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = p.stdout.readlines()
    code_result = p.wait()
    system = result[0].rstrip("\n")
    return system


def getWindowsNameInterfaceForMacadress(macadress):
    obj = utils.simplecommand("wmic NIC get MACAddress,NetConnectionID")
    for lig in obj["result"]:
        l = lig.lower()
        mac = macadress.lower()
        if l.startswith(mac):
            element = lig.split(" ")
            element[0] = ""
            fin = [x for x in element if x.strip() != ""]
            return " ".join(fin)


def getUserName():
    if sys.platform.startswith("linux"):
        obj = utils.simplecommand("who | cut -d" "  -f1 | uniq")
