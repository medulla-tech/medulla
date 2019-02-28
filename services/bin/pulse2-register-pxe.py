#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2015 siveo, http://www.siveo.net
# $Id$
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2. If not, see <http://www.gnu.org/licenses/>.
#
#"""
#This module is dedicated to analyse inventories sent by a Pulse 2 Client.
#The original inventory is sent using one line per kind of
#"""
import select
import socket
import pyinotify
import time
import gzip
import os
import re
import json
import datetime
from pulse2.package_server.config import P2PServerCP
from mmc.site import mmcconfdir
import sys
import ConfigParser
import logging
import getopt
import xml.etree.cElementTree as ET
import traceback
import magic

conf ={}
logoutput = open("/var/log/mmc/pulse2-register-pxe.log", "a")


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/var/log/mmc/pulse2-register-pxe.log',
                    filemode='w')



def subnetForIpMask(ip, netmask):
    result=[]
    try:
        ip = map(lambda x: int(x), ip.split('.'))
        netmask = map(lambda x: int(x), netmask.split('.'))
        for i in range(4):
            result.append( str(ip[i] & netmask[i]))
        result=".".join(result)
        return True, result
    except ValueError:
        return False, "O.O.O.O"

def tmpfile(name,string):
    if(logging.getLogger().getEffectiveLevel()<=logging.DEBUG):
        z=open("/tmp/%s"%name,"w")
        z.write(string)
        z.close()



def parsejsoninventory(file, file_content):
    tmpfile("content.txt",file_content)

    file_content = file_content.decode('ascii', errors='ignore')

    listcaractere=['\x07','\x00','\\r','\\n','\\t']
    for c in listcaractere:
        file_content= file_content.replace(c, '')
    file_content= file_content.replace('][', '],[')
    file_content= file_content.replace('}{', '},{')

    tmpfile("content1.txt",file_content)
    file_content = re.sub('[a-z0-9]*cpu\{',  '', file_content)
    z1 = re.compile("\}[a-z0-9]*pxe\{").split(file_content)
    if len(z1) > 1:
        z1[0] = "{" + z1[0] + "}"
        tmpfile("cpu.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            cpu=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("cpu\n%s"%cpu)
        except Exception as e:
            logging.getLogger().error("Error loading json cpu %s"%str(e))
            traceback.print_exc(file=logoutput)
    else:
        z1.insert(0, "")


    z1 = re.compile("\}[a-z0-9]*syslinux\{").split(z1[1])
    if len(z1) > 1:
        z1[0] = "{" + z1[0] + "}"
        tmpfile("pxe.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            pxe = json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("pxe\n%s"%pxe)
        except Exception as e:
            traceback.print_exc(file=logoutput)
            logging.getLogger().error("Error loading json pxe %s"%str(e))
    else:
        z1.insert(0, "")

    z1 = re.compile("\}[a-z0-9]*vpd\{").split(z1[1])
    if len(z1) > 1:
        z1[0] = "{" + z1[0] + "}"
        tmpfile("syslinux.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            syslinux=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("syslinux\n%s"%syslinux)
        except Exception as e:
            traceback.print_exc(file=logoutput)
            logging.getLogger().error("Error loading json syslinux %s"%str(e))
    else:
        z1.insert(0, "")

    z1 = re.compile("\}[a-z0-9]*vesa\{").split(z1[1])
    if len(z1) > 1:
        z1[0] = "{" + z1[0] + "}"
        tmpfile("vpd.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            vpd=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("vpd\n%s"%vpd)
        except Exception as e:
            traceback.print_exc(file=logoutput)
            logging.getLogger().error("Error loading json vpd %s"%str(e))
    else:
        z1.insert(0, "")

    z1 = re.compile("\}[a-z0-9]*disks\{").split(z1[1])
    if len(z1) > 1:
        z1[0]=str(z1[0])
        z1[0]= z1[0].replace('}{', '},{')
        z1[0]="[\n{" + str(z1[0]) + "}\n]"
        tmpfile("vesa.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            vesa=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("vesa\n%s"%vesa)
        except Exception as e:
            logging.getLogger().error("Error loading json vesa %s"%str(e))
    else:
        z1.insert(0, "")
    information = z1
    z1 = re.compile("\][a-z0-9]*dmi\{").split(z1[1])
    if len(z1) > 1:
        z1[0]= "{" + z1[0] + "]"
        z1[0]= z1[0].replace('}[', '},[')
        z1[0]= z1[0].replace('][', '],[')
        z1[0]= "[\n" + z1[0] + "\n]"
        tmpfile("disks.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            disks=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("disks\n%s"%disks)
        except Exception as e:
            traceback.print_exc(file=logoutput)
            logging.getLogger().error("Error loading json disks %s"%str(e))
    else:
        z1 = information
        z1 = re.compile("\}[a-z0-9]*dmi\{").split(z1[1])
        if len(z1) > 1:
            z1[0]= "{" + z1[0] + "}"
            z1[0]= z1[0].replace('}[', '},[')
            z1[0]= z1[0].replace('][', '],[')
            z1[0]= "[\n" + z1[0] + "\n]"
            tmpfile("disks.txt",z1[0])
            try:
                logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
                disks=json.loads(str(z1[0]), strict=False)
                logging.getLogger().debug("disks\n%s"%disks)
            except Exception as e:
                traceback.print_exc(file=logoutput)
                logging.getLogger().error("Error loading json disks %s"%str(e))
        else:
            z1.insert(0, "")

    z1 = re.compile("\}[a-z0-9]*memory\{").split(z1[1])
    if len(z1) > 1:
        z1[0] = "[\n{" + z1[0] + "}\n]"
        z1[0]= z1[0].replace('}{', '},{')
        z1[0]= z1[0].replace('][', '],[')
        tmpfile("dmi.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            dmi=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("dmi\n%s"%dmi)
        except Exception as e:
            traceback.print_exc(file=logoutput)
            logging.getLogger().error("Error loading json dmi %s"%str(e))
    else:
        z1.insert(0, "")

    z1 = re.compile("\}[a-z0-9]*pci\{").split(z1[1])
    if len(z1) > 1:
        z1[0] = "[\n{" + z1[0] + "}\n]"
        z1[0]= z1[0].replace('}{', '},{')
        z1[0]= z1[0].replace('][', '],[')
        tmpfile("memory.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            memory=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("memory\n%s"%memory)
        except Exception as e:
            traceback.print_exc(file=logoutput)
            logging.getLogger().error("Error loading json memory %s"%str(e))
    else:
        z1.insert(0, "")

    z1 = re.compile("\}[a-z0-9]*acpi\{").split(z1[1])
    if len(z1) > 1:
        z1[0] = "[" + "{" + z1[0] + "}"+ "]"
        z1[0]= z1[0].replace('}{', '},{')
        z1[0]= z1[0].replace('][', '],[')
        tmpfile("pci.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            pci=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("pci\n%s"%pci)
        except Exception as e:
            traceback.print_exc(file=logoutput)
            logging.getLogger().error("Error loading json pci %s"%str(e))
    else:
        z1.insert(0, "")


    z1 = re.compile("\][a-z0-9]*kernel\[").split(z1[1])
    if len(z1) > 1:
        z1[0]= z1[0].replace('}[', '},[')
        z1[0]= z1[0].replace('][', '],[')
        z1[0]= "[\n" + "{" + z1[0]+ "]\n"+ "]"
        tmpfile("acpi.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            acpi=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("acpi\n%s"%acpi)
        except Exception as e:
            traceback.print_exc(file=logoutput)
            logging.getLogger().error("Error loading json acpi %s"%str(e))
    else:
        z1.insert(0, "")

    z1 = re.compile("\][a-z0-9]*hdt\{").split(z1[1])
    if len(z1) > 1:
        tmpfile("kernel.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            kernel=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("kernel\n%s"%kernel)
        except Exception as e:
            traceback.print_exc(file=logoutput)
            logging.getLogger().error("Error loading json kernel %s"%str(e))
    else:
        z1.insert(0, "")

    z1 = re.compile("\}[a-z0-9]*hostname\{").split(z1[1])
    if len(z1) > 1:
        z1[0]= "{" + str(z1[0]) + "}"
        tmpfile("hdt.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            hdt=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("hdt\n%s"%hdt)
        except Exception as e:
            traceback.print_exc(file=logoutput)
            logging.getLogger().error("Error loading json hdt %s"%str(e))
    else:
        z1.insert(0, "")

    z1 = re.compile("\}[a-z0-9]*TRAILER!!!").split(z1[1])
    if len(z1) > 1:
        z1[0]= "{" + z1[0]+ "}"
        tmpfile("hostname.txt",z1[0])
        try:
            logging.getLogger().debug("Trying to load:\n%s"%str(z1[0]))
            hostname=json.loads(str(z1[0]), strict=False)
            logging.getLogger().debug("hostname\n%s"%hostname)
        except Exception as e:
            traceback.print_exc(file=logoutput)
            logging.getLogger().error("Error loading json hostname %s"%str(e))
    else:
        z1.insert(0, "")
    ##############REQUEST##############

    date = '{:%Y-%m-%d-%H-%M-%S}'.format(datetime.datetime.now())
    REQUEST = ET.Element("REQUEST")
    DEVICEID = ET.SubElement(REQUEST, "DEVICEID").text = hostname['hostname.hostname']+'-'+date
    QUERY = ET.SubElement(REQUEST, "QUERY").text = "INVENTORY"
    TAG = ET.SubElement(REQUEST, "TAG").text = "root"
    CONTENT = ET.SubElement(REQUEST, "CONTENT")

    ##############ACCESSLOG##############

    ACCESSLOG = ET.SubElement(CONTENT, "ACCESSLOG")
    LOGDATE = ET.SubElement(ACCESSLOG, "LOGDATE").text='{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    USERID = ET.SubElement(ACCESSLOG, "USERID").text='N/A'

    ##############BIOS##############

    BIOS = ET.SubElement(CONTENT, "BIOS")
    ASSETTAG = ET.SubElement(BIOS, "ASSETTAG").text ="No Asset Information"
    MMANUFACTURER = ET.SubElement(BIOS, "MMANUFACTURER").text = dmi[1]['dmi.base_board.manufacturer']
    MMODEL = ET.SubElement(BIOS, "MMODEL").text = dmi[1]['dmi.base_board.product_name']
    MSN = ET.SubElement(BIOS, "MSN").text = dmi[1]['dmi.base_board.serial']
    if not dmi[2]['dmi.system.sku_number'].strip() == '':
        SKUNUMBER = ET.SubElement(BIOS, "SKUNUMBER").text = dmi[2]['dmi.system.sku_number']
    BDATE = ET.SubElement(BIOS, "BDATE").text = dmi[3]['dmi.bios.release_date']
    BMANUFACTURER = ET.SubElement(BIOS, "BMANUFACTURER").text = dmi[1]['dmi.base_board.manufacturer']
    BVERSION = ET.SubElement(BIOS, "BVERSION").text = dmi[3]['dmi.bios.version']
    if not dmi[2]['dmi.system.manufacturer'].strip() == '':
        SMANUFACTURER = ET.SubElement(BIOS, "SMANUFACTURER").text = dmi[2]['dmi.system.manufacturer']
    if not dmi[2]['dmi.system.product_name'].strip() == '':
        SMODEL = ET.SubElement(BIOS, "SMODEL").text = dmi[2]['dmi.system.product_name']
    if not dmi[2]['dmi.system.serial'].strip() == '':
        SSN = ET.SubElement(BIOS, "SSN").text = dmi[2]['dmi.system.serial']

    ##############HARDWARE##############
    HARDWARE = ET.SubElement(CONTENT, "HARDWARE")
    CHASSIS_TYPE = ET.SubElement(HARDWARE, "CHASSIS_TYPE").text = dmi[4]['dmi.chassis.type']
    IPADDR = ET.SubElement(HARDWARE, "IPADDR").text = pxe['pxe.ipaddr']
    DEFAULTGATEWAY = ET.SubElement(HARDWARE, "DEFAULTGATEWAY").text = conf['pxe_gateway']
    NAME = ET.SubElement(HARDWARE, "NAME").text = hostname['hostname.hostname']
    UUID = ET.SubElement(HARDWARE, "UUID").text =  dmi[2]['dmi.system.uuid']
    OSNAME = ET.SubElement(HARDWARE, "OSNAME").text = "Unknown operating system (PXE network boot inventory)"
    listcpu_model = cpu["cpu.model"].split()
    freqcpu_info=str(listcpu_model.pop())
    PROCESSORS = ET.SubElement(HARDWARE,'PROCESSORS').text = freqcpu_info
    PROCESSORN = ET.SubElement(HARDWARE,'PROCESSORN').text = str(cpu["cpu.num_cores"])
    PROCESSORT = ET.SubElement(HARDWARE,'PROCESSORT').text = str(cpu["cpu.model_id"])

    ##############NETWORKS##############

    NETWORKS = ET.SubElement(CONTENT, "NETWORKS")
    DESCRIPTION = ET.SubElement(NETWORKS,'DESCRIPTION').text = 'eth0'
    IPADDRESS = ET.SubElement(NETWORKS,'IPADDRESS').text = pxe['pxe.ipaddr']
    MACADDR = ET.SubElement(NETWORKS,'MACADDR').text = pxe['pxe.mac_addr']
    IPMASK = ET.SubElement(NETWORKS,'IPMASK').text = conf['pxe_mask']
    IPGATEWAY = ET.SubElement(NETWORKS,'IPGATEWAY').text = conf['pxe_gateway']
    IPSUBNET = ET.SubElement(NETWORKS,'IPSUBNET').text = conf['pxe_subnet']
    STATUS = ET.SubElement(NETWORKS,'STATUS').text = 'Up'
    TYPE = ET.SubElement(NETWORKS,'TYPE').text = 'Ethernet'
    VIRTUALDEV = ET.SubElement(NETWORKS,'VIRTUALDEV').text = '0'

    ##############STORAGES##############

    nombredisk=len(disks)-1
    if nombredisk >=1 :
        for diskid in range(1,nombredisk+1):
            STORAGES = ET.SubElement(CONTENT, "STORAGES")
            NAME = ET.SubElement(STORAGES, "NAME").text='hd'+str(diskid)
            TYPE = ET.SubElement(STORAGES, "TYPE").text='disk'
            regex_unit = re.compile(r'[[^0-9. ]')
            regex_size = re.compile(r'[[^a-zA-Z ]')
            disk_unit = regex_unit.sub("",disks[diskid][0]['disk->size'])
            disk_size = regex_size.sub("",disks[diskid][0]['disk->size'])
            if disk_unit == 'TiB':
                disk_size = str(int(float(disk_size))*1000000)
            elif disk_unit == 'GiB':
                disk_size = str(int(float(disk_size))*1000)
            else:
                disk_size = str(int(float(disk_size)))
            DISKSIZE = ET.SubElement(STORAGES, "DISKSIZE").text=disk_size

    ##############DRIVES##############

        for diskid in range(1,nombredisk+1):
            nbpartition = len(disks[diskid])-1
            if nbpartition >=1 :
                for partitionid in range(1,nbpartition+1):
                    DRIVES = ET.SubElement(CONTENT, "DRIVES")
                    try:
                        FILESYSTEM = ET.SubElement(DRIVES,'FILESYSTEM').text=disks[diskid][partitionid]['partition->type']
                        regex_unit = re.compile(r'[[^0-9. ]')
                        regex_size = re.compile(r'[[^a-zA-Z ]')
                        partition_unit = regex_unit.sub("",disks[diskid][partitionid]['partition->size'])
                        partition_size = regex_size.sub("",disks[diskid][partitionid]['partition->size'])
                        if partition_unit == 'TiB':
                            partition_size = str(int(float(partition_size))*1000000)
                        elif partition_unit == 'GiB':
                            partition_size = str(int(float(partition_size))*1000)
                        else:
                            partition_size = str(int(float(partition_size)))
                        TOTAL = ET.SubElement(DRIVES,'TOTAL').text=partition_size
                        TYPE = ET.SubElement(DRIVES,'TYPE').text=disks[diskid][partitionid]['partition->os_type']
                    except Exception as e:
                        traceback.print_exc(file=logoutput)
                        logging.getLogger().warn("Unrecognized Partition Layout disk %s partition%s %s"%(diskid, partitionid, str(e)))
    xmlstring = ET.tostring(REQUEST)
    return  '<?xml version="1.0" encoding="utf-8"?>' + xmlstring


def senddata(query,ip ="127.0.0.1", port =1001 ):
    adresse=(ip,port)
    monSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.getLogger().debug("Send PXE xml for registration :%s"% query)
    monSocket.sendto("\xBB%s" % query, adresse)
    time.sleep(conf['pxe_timesenddata'])
    monSocket.sendto("\xBA%s" % query, adresse)
    time.sleep(conf['pxe_timesenddata'])
    monSocket.sendto("\xBA%s" % query, adresse)
    monSocket.close()

def mac_adressexmlinformationsimple(file_content):
    root = ET.fromstring(file_content)
    addr=[]
    for child in root:
        if child.tag == "CONTENT":
            for cc in child:
                if cc.tag == "NETWORKS":
                    for dd in cc:
                        if dd.tag == "MACADDR":
                            if dd.text !='00:00:00:00:00:00':
                                addr.append(dd.text)
    addr=list(set(addr))
    if len(addr) > 1:
        logging.getLogger().debug("several mac address found : %s"%addr)
    if len(addr) == 1:
        logging.getLogger().debug("<MACADDR> selected : %s"%addr[0])
        return addr[0]
    else:
        return None

def macadressclear(file_content, interface_mac_clear):
    root = ET.fromstring(file_content)
    boolremoveelement = False
    for child in root:
        if child.tag == "CONTENT":
            for network in child.findall('NETWORKS'):
                for dd in network:
                    if dd.tag == "MACADDR" and dd.text == interface_mac_clear:
                        boolremoveelement = True
                        child.remove(network)
                        break
    if boolremoveelement:
        logging.getLogger().debug("Clear interface with macadress %s "%interface_mac_clear)
        xml_str =  ET.tostring(root).encode("ASCII", 'ignore')
        logging.getLogger().debug("New xml netwrok : %s"%xml_str)
        xml_str = xml_str.replace('\n', '')
        return xml_str
        pass
    return  file_content

def mac_adressexmlpxe(file_content):
    root = ET.fromstring(file_content)
    addr=[]
    for child in root:
        if child.tag == "CONTENT":
            for cc in child:
                if cc.tag == "NETWORKS":
                    for dd in cc:
                        if dd.tag == "MACADDRPXE":
                            if dd.text !='00:00:00:00:00:00':
                                logging.getLogger().debug("<MACADDRPXE> selected : %s"%dd.text)
                                return dd.text

    logging.getLogger().debug("no interface report for PXE")
    return None

def mac_adressexml(file_content):
    macadrss = mac_adressexmlpxe(file_content)
    if macadrss != None:
        return macadrss
    else:
        macadrss = mac_adressexmlinformationsimple(file_content)
        if macadrss != None:
            return macadrss
    logging.getLogger().error("Mac adress Mising return '00:00:00:00:00:00'")
    return '00:00:00:00:00:00'

class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_ACCESS(self, event):
        print "ACCESS event:", event.pathname

    def process_IN_ATTRIB(self, event):
        print "ATTRIB event:", event.pathname

    def process_IN_CLOSE_NOWRITE(self, event):
        print "CLOSE_NOWRITE event:", event.pathname

    def process_IN_CLOSE_WRITE(self, event):
        print "CLOSE_WRITE event:", event.pathname

    def process_IN_CREATE(self, event):
        logging.getLogger().debug("CREATE event:%s"% event.pathname)
        time.sleep(0.005)
        self.traitement(event.pathname)

    def process_IN_DELETE(self, event):
        print "DELETE event:", event.pathname

    def process_IN_MODIFY(self, event):
        logging.getLogger().debug("MODIFY event: %s"% event.pathname)
        time.sleep(0.025)
        self.traitement(event.pathname)

    def process_IN_OPEN(self, event):
        print "OPEN event:"

    def traitement(self, name):

        if os.path.isfile(str(name)):
            file_content=""
            file_content1=""
            logging.getLogger().info("parse inventory %s",name)

            try:
                if ( magic.detect_from_filename(name).mime_type == 'application/gzip' ):
                    com='zcat %s'%name
                    file_content1 =  os.popen(com).read()
                    file_content=parsejsoninventory(str(name),file_content1)
                else:
                    with open(name, 'r') as content_file:
                        file_content=content_file.read().replace('\n', '')

                m = re.search('<REQUEST>.*<\/REQUEST>', file_content)
                file_content = str(m.group(0))
                try:
                    file_content = macadressclear(file_content, "00:00:00:00:00:00")
                    mac = mac_adressexml(file_content)
                    try:
                        # add Mc:mac address end of datagram
                        header='<?xml version="1.0" encoding="utf-8"?>'
                        file_content=file_content[:-10]
                        xmldata="%s%sMc:%s</REQUEST>"%(header,file_content,mac)
                        logging.getLogger().debug("XML recv from pxe client %s"% xmldata)
                        os.remove(name)
                        senddata(xmldata,'127.0.0.1',conf['port'])
                    except Exception as e:
                        traceback.print_exc(file=logoutput)
                        logging.getLogger().error("UDP error sending to %s:%d [%s]"%('127.0.0.1', conf['port'], str(e)))
                except Exception as e:
                    traceback.print_exc(file=logoutput)
                    logging.getLogger().error("MAC address error %s"%str(e))
            except Exception as e:
                traceback.print_exc(file=logoutput)
                logging.getLogger().error("Error traitement file %s"%str(name))
                logging.getLogger().error("Error traitement %s"%str(e))

class watchInventory:
    def __init__(self):
        self.eh = MyEventHandler()
        logging.getLogger().info("install inotify")

    def run(self):
        self.wm = pyinotify.WatchManager()
        self.notifier = pyinotify.ThreadedNotifier(self.wm, self.eh)
        self.notifier.start()
        mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY  # watched eventspyinotify.IN_DELETE |
        self.wm.add_watch( '/var/lib/pulse2/imaging/inventories',mask, rec=True)
        logging.getLogger().info("watch event /var/lib/pulse2/imaging/inventories")

    def stop(self):
        self.notifier.stop()

if __name__ == '__main__':
    logging.getLogger().info("Start pulse2-register-pxe.py")
    inifile = mmcconfdir + "/pulse2/package-server/package-server.ini"
    pidfile="/var/run/pulse2-register-pxe.pid"
    cp = None
    try:
        opts, suivarg = getopt.getopt(sys.argv[1:], "f:dh")
    except getopt.GetoptError:
        sys.exit(2)
    daemonize = True
    for option, argument in opts:
        if option == "-f":
            inifile = argument
        elif option == "-d":
            logging.getLogger().info("logger mode debug")
            daemonize = False
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logging.getLogger().addHandler(ch)
            logging.getLogger().setLevel(logging.DEBUG)
            print "pid file: %d\n"%os.getpid()
            print "kill -9 %s"%os.getpid()
        elif option == "-h":
            print "Configure in file '%s' \n[imaging_api]\npxe_port=???\n "%inifile
            print "\t<launch program> [option]\n"
            print "\t[-f <file configuration>]\n\t[-d] debug mode no daemonized"
            sys.exit(0)
    if not os.path.exists(inifile):
        print "File '%s' does not exist." % inifile
        sys.exit(3)
    cp = ConfigParser.ConfigParser()
    cp.read(inifile)
    cp.read(inifile + '.local')

    conf['ip']="127.0.0.1"
    if cp.has_option('imaging_api', 'pxe_port'):
        conf['port'] = int(cp.get('imaging_api', 'pxe_port'))
    else:
        conf['port'] = 1001

    if cp.has_option("main", "bind"):  # TODO remove in a future version
        logging.getLogger().warning("'bind' is obsolete, please replace it in your config file by 'host'")
        bind = cp.get("main", 'bind')
    elif cp.has_option('main', 'host'):
        bind = cp.get("main", 'host')

    if cp.has_option('main', 'public_ip'):
        public_ip = cp.get("main", 'public_ip')
    else:
        public_ip = bind

    if cp.has_option('main', 'public_mask'):
        public_mask = cp.get("main", 'public_mask')
    else:
        public_mask = '255.255.255.0'

    if cp.has_option('imaging_api', 'pxe_mask'):
        conf['pxe_mask'] = cp.get('imaging_api', 'pxe_mask')
    else:
        conf['pxe_mask'] = public_mask

    if  cp.has_option('imaging_api', 'pxe_gateway'):
        conf['pxe_gateway'] = cp.get("imaging_api", 'pxe_gateway')
    else:
        conf['pxe_gateway'] = public_ip

    if  cp.has_option('imaging_api', 'pxe_timesenddata'):
        conf['pxe_timesenddata'] = cp.getfloat("imaging_api", 'pxe_timesenddata')
    else:
        conf['pxe_timesenddata'] = 1

    if cp.has_option('imaging_api', 'pxe_tftp_ip'):
        conf['pxe_tftp_ip'] = cp.get('imaging_api', 'pxe_tftp_ip')
    else:
        conf['pxe_tftp_ip'] = public_ip
        logging.getLogger().info("pxe_tftp_ip option is not defined and has been set to public_ip. If incorrect, please configure pxe_tftp_ip in imaging_api section of [%s].local"%inifile)
        print "pxe_tftp_ip option is not defined and has been set to public_ip. If incorrect, please configure pxe_tftp_ip in imaging_api section of [%s].local"%inifile
    if not daemonize:
        if  cp.has_option('imaging_api', 'pxe_debug'):
            if cp.getboolean("imaging_api", 'pxe_debug'):
                logging.getLogger().info("logger mode debug")
                conf['pxe_debug']=logging.DEBUG
                logging.getLogger().setLevel(logging.DEBUG)
            else:
                mode = logging.WARNING
                conf['pxe_debug']=logging.WARNING
                logging.getLogger().setLevel(logging.WARNING)
    else:
        conf['pxe_debug']=logging.DEBUG

    if  cp.has_option('imaging_api', 'pxe_subnet'):
        conf['pxe_subnet'] = cp.get("imaging_api", 'pxe_subnet')
    else:
        a, b = subnetForIpMask( conf['pxe_tftp_ip'], conf['pxe_mask'] )
        conf['pxe_subnet'] = b
    logging.getLogger().info("configuration : %s"%conf)

    if daemonize:
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            print >>sys.stderr, "Fork #1 failed: %d (%s)" % (e.errno, e.strerror)
            sys.exit(1)
        # dissociate from parent environment
        os.close(sys.stdin.fileno())
        os.close(sys.stdout.fileno())
        os.close(sys.stderr.fileno())
        os.chdir("/")
        os.setsid()
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent, print eventual PID before
                print "Daemon PID %d" % pid
                print "kill -9 $(cat %s"%pidfile
                logging.getLogger().info("Daemon PID %d" % pid)
                os.seteuid(0)
                os.setegid(0)
                logging.getLogger().info("PID file" + str(pid) + " > " + pidfile)
                logging.getLogger().info("kill -9 $(cat %s)"%pidfile)
                os.system("echo " + str(pid) + " > " + pidfile)
                sys.exit(0)
        except OSError, e:
            print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
            sys.exit(1)
    try:
        a = watchInventory()
        a.run()
    except KeyboardInterrupt:
        a.stop()
        sys.exit(3)
