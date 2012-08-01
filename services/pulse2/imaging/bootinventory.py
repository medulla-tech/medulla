# -*- coding: utf-8; -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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


"""
This module is dedicated to analyse inventories sent by a Pulse 2 Client.
The original inventory is sent using one line per kind of
"""

import re # the main job here : doing regex !
import time

# here are the regex
MACADDR_RE  = re.compile("^MAC Address:(.+)$") # MAC Address
IPADDR_RE   = re.compile("^IP Address:(.+):([0-9]+)$") # IP Address:port
MEM_INFO_RE = re.compile("^M:([0-9a-f]+),U:([0-9a-f]+)$") # lower / upper mem
BUS_INFO_RE = re.compile("^B:([0-9A-Fa-f]+),f:([0-9A-Fa-f]+),v:([0-9A-Fa-f]+),d:([0-9A-Fa-f]+),c:([0-9A-Fa-f]+),s:([0-9A-Fa-f]+)$") # bus, dev, vendor, device, class, subclass
DISKINFO_RE = re.compile("^D:\(hd([0-9]+)\):CHS\(([0-9]+),([0-9]+),([0-9]+)\)=([0-9]+)$") # number, CHS, size
PARTINFO_RE = re.compile("^P:([0-9]+),t:([0-9a-f]+),s:([0-9]+),l:([0-9]+)$") # number, type, start, len
BIOSINFO_RE = re.compile("^S0:([^\|]*)\|([^\|]*)\|([^\|]*)$") # 3 components : vendor, version, date
SYSINFO_RE  = re.compile("^S1:([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([0-9A-F]{32})$") # 5 components : vendor, desc, ??, ??, UUID (16 hex chars)
ENCLOS_RE   = re.compile("^S3:([^\|]*)\|([0-9]+)$") # vendor, type
MEMSLOT_RE  = re.compile("^SM:([0-9]+):([0-9]+):([^:]*):([0-9]+):([0-9]+)$") # Size in MB, Form factor, Location, Type, Speed in MHZ
NUMCPU_RE   = re.compile("^S4:([0-9]+)$") # CPU number
FEATCPU_RE  = re.compile("^C:(.*)$") # CPU features, comma-separated
FREQCPU_RE  = re.compile("^F:([0-9]+)$") # CPU frequency

OCS_TPL = """<?xml version="1.0" encoding="UTF-8"?>
<REQUEST>
  <CONTENT>
    <ACCESSLOG>
      <LOGDATE>%s</LOGDATE>
      <USERID>N/A</USERID>
    </ACCESSLOG>
    <BIOS>
      <ASSETTAG></ASSETTAG>
      <BDATE>%s</BDATE>
      <BMANUFACTURER>%s</BMANUFACTURER>
      <BVERSION>%s</BVERSION>
      <SMANUFACTURER>%s</SMANUFACTURER>
      <SMODEL></SMODEL>
      <SSN></SSN>
    </BIOS>
    <HARDWARE>
      <ARCHNAME></ARCHNAME>
      <CHECKSUM></CHECKSUM>
      <DATELASTLOGGEDUSER></DATELASTLOGGEDUSER>
      <DEFAULTGATEWAY></DEFAULTGATEWAY>
      <DESCRIPTION></DESCRIPTION>
      <DNS></DNS>
      <ETIME></ETIME>
      <IPADDR>%s</IPADDR>
      <LASTLOGGEDUSER></LASTLOGGEDUSER>
      <MEMORY></MEMORY>
      <NAME>%s</NAME>
      <OSCOMMENTS></OSCOMMENTS>
      <OSNAME></OSNAME>
      <OSVERSION></OSVERSION>
      <PROCESSORN></PROCESSORN>
      <PROCESSORS>%s</PROCESSORS>
      <PROCESSORT></PROCESSORT>
      <SWAP></SWAP>
      <USERID></USERID>
      <UUID></UUID>
      <VMSYSTEM></VMSYSTEM>
      <WORKGROUP></WORKGROUP>
    </HARDWARE>
    <NETWORKS>
      <DESCRIPTION></DESCRIPTION>
      <DRIVER></DRIVER>
      <IPADDRESS>%s</IPADDRESS>
      <IPDHCP></IPDHCP>
      <IPGATEWAY></IPGATEWAY>
      <IPMASK></IPMASK>
      <IPSUBNET></IPSUBNET>
      <MACADDR>%s</MACADDR>
      <PCISLOT></PCISLOT>
      <STATUS>Up</STATUS>
      <TYPE>Ethernet</TYPE>
      <VIRTUALDEV></VIRTUALDEV>
    </NETWORKS>
  </CONTENT>
  <DEVICEID>%s</DEVICEID>
  <QUERY>INVENTORY</QUERY>
  <TAG>%s</TAG>
</REQUEST>"""

class BootInventory:
    """
        Class holding one inventory.

        Two functions of interest :
          - load() => fill this object using data from the client
          - dump() => dump a struct representing the object

    """
    #######################
    # this class property #
    #######################
    # memory info (lower/upper), in bytes
    mem_info        = {'lower' : 0, 'upper': 0}
    # periphericals
    bus_info        = {}
    # disks (and parts)
    disk_info       = {}
    # bios basic infos
    bios_info       = {'vendor': '', 'version': '', 'date' : ''}
    # system basic infos
    sys_info        = {'manufacturer': '', 'product': '', 'version' : '', 'serial' : '', 'uuid' : ''}
    # enclosure basic infos
    enclos_info     = {'vendor': '', 'type': ''}
    # memory slot used
    memslot_info    = {'size' : 0, 'ff': 0, 'location': '', 'type': '', 'speed': 0}
    # number of (logical) CPU, f.e 4 on a core 2 Duo
    numcpu_info     = 0
    # CPu features, to be interpreted (that's a infamous 26 bytes array)
    featcpu_info    = []
    # the CP frequencies
    freqcpu_info    = []
    # the client MAC adress
    macaddr_info    = ''
    # the inventory IP source (not necesary the client IP)
    ipaddr_info     = {'ip': '', 'port': 0}
    unprocessed     = []

    def __init__(self, data = None):
        """
        Object creator

        @param data : the initial inventory data
        """
        if data != None :
            self.load(data)

    def __str__(self):
        """
        Return a string version of this object
        """
        return self.dump().__str__()

    def load(self, data):
        """
        Load the inventory data nito the object

        @param data : the inventory data
        """
        current_disk = None # track the disk we are reading

        for line in data: # process line per line
            if not len(line):
                continue

            # then attempts to process line per line

            mo = re.match(MEM_INFO_RE, line)
            if mo :
                self.mem_info['lower'] = int(mo.group(1), 16)
                self.mem_info['upper'] = int(mo.group(2), 16)
                continue

            mo = re.match(BUS_INFO_RE, line)
            if mo :
                bus = str(int(mo.group(1), 16))
                dev = str(int(mo.group(2), 16))
                vendor = int(mo.group(3), 16)
                device = int(mo.group(4), 16)
                cl = int(mo.group(5), 16)
                subcl = int(mo.group(6), 16)
                if not bus in self.bus_info:
                    self.bus_info[bus] = dict()
                self.bus_info[bus][dev] = {
                    "vendor": vendor,
                    "device" : device,
                    "class" : cl,
                    "subclass" : subcl}
                continue

            mo = re.match(DISKINFO_RE, line)
            if mo :
                num = str(int(mo.group(1), 10))
                c = int(mo.group(2), 10)
                h = int(mo.group(3), 10)
                s = int(mo.group(4), 10)
                sz = int(mo.group(4), 10)
                self.disk_info[num] = {
                    "C": c,
                    "H" : h,
                    "S" : s,
                    "size" : sz,
                    "parts" : dict()}
                current_disk = num
                continue

            mo = re.match(PARTINFO_RE, line)
            if mo :
                num = str(int(mo.group(1), 10))
                t = int(mo.group(2), 16)
                s = int(mo.group(3), 10)
                l = int(mo.group(4), 10)
                self.disk_info[current_disk]['parts'][num] = {
                    'type' : t,
                    'start' : s,
                    'length' : l}
                continue

            mo = re.match(BIOSINFO_RE, line)
            if mo :
                self.bios_info['vendor'] = mo.group(1)
                self.bios_info['version'] = mo.group(2)
                self.bios_info['date'] = mo.group(3)
                continue

            mo = re.match(SYSINFO_RE, line)
            if mo :
                self.sys_info['manufacturer'] = mo.group(1)
                self.sys_info['product'] = mo.group(2)
                self.sys_info['version'] = mo.group(3)
                self.sys_info['serial'] = mo.group(4)
                self.sys_info['uuid'] = mo.group(5)
                continue

            mo = re.match(ENCLOS_RE, line)
            if mo :
                self.enclos_info['vendor'] = mo.group(1)
                self.enclos_info['type'] = mo.group(2)
                continue

            mo = re.match(MEMSLOT_RE, line)
            if mo :
                self.memslot_info['size'] = int(mo.group(1), 10)
                self.memslot_info['ff'] = int(mo.group(2), 10)
                self.memslot_info['location'] = mo.group(3)
                self.memslot_info['type'] = mo.group(4)
                self.memslot_info['speed'] = int(mo.group(5), 10)
                continue

            mo = re.match(NUMCPU_RE, line)
            if mo :
                self.numcpu_info = int(mo.group(1), 10)
                continue

            mo = re.match(FEATCPU_RE, line)
            if mo :
                self.featcpu_info = map(lambda x: int(x, 16), mo.group(1).split(','))
                continue

            mo = re.match(FREQCPU_RE, line)
            if mo :
                self.freqcpu_info = int(mo.group(1), 10)
                continue

            mo = re.match(MACADDR_RE, line)
            if mo :
                self.macaddr_info = mo.group(1)
                continue

            mo = re.match(IPADDR_RE, line)
            if mo :
                self.ipaddr_info['ip'] = mo.group(1)
                self.ipaddr_info['port'] = int(mo.group(2), 10)
                continue

            self.unprocessed.append(line) # finally, store lines which didn't match

    def dump(self):
        """
        Return a dict with this object values
        """
        return {
            'mem'       : self.mem_info,
            'bus'       : self.bus_info,
            'disk'      : self.disk_info,
            'bios'      : self.bios_info,
            'sys'       : self.sys_info,
            'enclos'    : self.enclos_info,
            'memslot'   : self.memslot_info,
            'numcpu'    : self.numcpu_info,
            'featcpu'   : self.featcpu_info,
            'freqcpu'   : self.freqcpu_info,
            'macaddr'   : self.macaddr_info,
            'ipaddr'    : self.ipaddr_info}

    def dumpOCS(self, hostname, entity):
        """
        Return an OCS XML string
        """

        return OCS_TPL % (time.strftime("%Y-%m-%d %H:%M:%S"),
                          self.bios_info['date'],
                          self.bios_info['vendor'],
                          self.bios_info['version'],
                          self.bios_info['vendor'],
                          self.ipaddr_info['ip'],
                          hostname,
                          str(round(self.freqcpu_info / 1000)),
                          self.ipaddr_info['ip'],
                          self.macaddr_info,
                          "%s-%s" % (hostname, time.strftime("%Y-%m-%d-%H-%M-%S")),
                          entity)
