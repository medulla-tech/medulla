# -*- coding: utf-8; -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com
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
import xml.etree.ElementTree as ET  # form XML Building

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
MEMSLOT_RE  = re.compile("^SM:([0-9]+):([^:]*):([^:]*):([0-9]+):([0-9]+)$") # Size in MB, Form factor, Location, Type, Speed in MHZ
NUMCPU_RE   = re.compile("^S4:([0-9]+)$") # CPU number
FEATCPU_RE  = re.compile("^C:(.*)$") # CPU features, comma-separated
FREQCPU_RE  = re.compile("^F:([0-9]+)$") # CPU frequency

# Filesystems titles
FILESYSTEMS_H = {
	"00":"Empty",\
	"01":"FAT12",\
	"02":"XENIX root",\
	"03":"XENIX usr",\
	"04":"Small FAT16",\
	"05":"Extended",\
	"06":"FAT16",\
	"07":"HPFS/NTFS",\
	"08":"AIX",\
	"09":"AIX bootable",\
	"0a":"OS/2 boot manager",\
	"0b":"FAT32",\
	"0c":"FAT32 (LBA)",\
	"0e":"FAT16 (LBA)",\
	"0f":"Extended (LBA)",\
	"10":"OPUS",\
	"11":"Hidden FAT12",\
	"12":"Compaq diagnostics",\
	"14":"Hidden FAT16 (<32M)",\
	"16":"Hidden FAT16",\
	"17":"Hidden HPFS/NTFS",\
	"18":"AST SmartSleep",\
	"1b":"Hidden FAT32",\
	"1c":"Hidden FAT32 (LBA)",\
	"1d":"Hidden FAT16 (LBA)",\
	"24":"NEC DOS",\
	"39":"Plan 9",\
	"3c":"PartitionMagic recovery",\
	"40":"Venix 80286",\
	"41":"PPC PReP Boot",\
	"42":"SFS",\
	"4d":"QNX4.x",\
	"4e":"QNX4.x 2nd part",\
	"4f":"QNX4.x 3rd part",\
	"50":"OnTrack DM",\
	"51":"OnTrack DM6 Aux1",\
	"52":"CP/M",\
	"53":"OnTrack DM6 Aux3",\
	"54":"OnTrack DM6",\
	"55":"EZ Drive",\
	"56":"Golden Bow",\
	"5c":"Priam Edisk",\
	"61":"SpeedStor",\
	"63":"GNU HURD/SysV",\
	"64":"Netware 286",\
	"65":"Netware 386",\
	"70":"DiskSec MultiBoot",\
	"75":"PC/IX",\
	"80":"Minix (<1.4a)",\
	"81":"Minix (>1.4b)",\
	"82":"Linux swap",\
	"83":"Linux",\
	"84":"OS/2 Hidden C:",\
	"85":"Linux extended",\
	"86":"NTFS volume set",\
	"87":"NTFS volume set",\
	"88":"Linux plaintext",\
	"08":"Linux LVM",\
	"93":"Amoeba",\
	"94":"Amoeba BBT",\
	"9f":"BSD/OS",\
	"a0":"IBM Thinkpad hibernation",\
	"a5":"FreeBSD",\
	"a6":"OpenBSD",\
	"a7":"NeXTSTEP",\
	"a8":"Darwin UFS",\
	"a9":"NetBSD",\
	"ab":"Darwin boot",\
	"b7":"BSDI fs",\
	"b8":"BSDI swap",\
	"bb":"Boot Wizard Hid",\
	"be":"Solaris boot",\
	"bf":"Solaris",\
	"c1":"DRDOS/2 (FAT12)",\
	"c4":"DRDOS/2 (FAT16 <32M)",\
	"c6":"DRDOS/2 (FAT16)",\
	"c7":"Syrinx",\
	"da":"Non-FS data",\
	"db":"CP/M / CTOS",\
	"de":"Dell Utility",\
	"df":"BootIt",\
	"e1":"DOS access",\
	"e3":"DOS R/O",\
	"e4":"SpeedStor",\
	"eb":"BeOS fs",\
	"ee":"EFI GPT",\
	"ef":"EFI FAT",\
	"f0":"Linux/PA-RISC boot",\
	"f1":"SpeedStor",\
	"f2":"DOS secondary",\
	"f4":"SpeedStor",\
	"fd":"Linux RAID auto",\
	"fe":"LANstep",\
	"ff":"XENIX BBT" }

# Computer types titles
COMPUTER_TYPES = {
	"1":"Other",\
	"2":"Unknown",\
	"3":"Desktop",\
	"4":"Low Profile Desktop",\
	"5":"Pizza Box",\
	"6":"Mini Tower",\
	"7":"Tower",\
	"8":"Portable",\
	"9":"LapTop",\
	"a":"Notebook",\
	"b":"Hand Held",\
	"c":"Docking Station",\
	"d":"All in One",\
	"e":"Sub Notebook",\
	"f":"Space-saving",\
	"10":"Lunch Box",\
	"11":"Main Server Chassis",\
	"12":"Expansion Chassis",\
	"13":"SubChassis",\
	"14":"Bus Expansion Chassis",\
	"15":"Peripheral Chassis",\
	"16":"RAID Chassis",\
	"17":"Rack Mount Chassis",\
	"18":"Sealed-case PC",\
	"19":"Multi-system Chassis",\
	"1a":"Compact PCI",\
	"1b":"Advanced TCA",\
	"1c":"Blade",\
	"1d":"Blade Enclosure"}


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
    # memory info
    memory_info	    = []
    # number of (logical) CPU, f.e 4 on a core 2 Duo
    numcpu_info     = 0
    # CPu features, to be interpreted (that's a infamous 26 bytes array)
    featcpu_info    = []
    # the CP frequencies
    freqcpu_info    = 0
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
	self.memory_info = []

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
		lba_size = int(mo.group(5), 10)
                self.disk_info[num] = {
                    "C": c,
                    "H" : h,
                    "S" : s,
                    "size" : sz,
		    "lba_size" : lba_size,
		    "lba_size_mb" : lba_size*512/1000/1000,
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
		    'type_hex' : '%.2X' % t,
                    'start' : s,
		    'length_mb' : l*512/1000/1000,
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
		memslot_info = {}
                memslot_info['size'] = int(mo.group(1), 10)
                memslot_info['ff'] = mo.group(2)
                memslot_info['location'] = mo.group(3)
                memslot_info['type'] = int(mo.group(4),10)
                memslot_info['speed'] = int(mo.group(5), 10)
		self.memory_info += [memslot_info]
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
            'memslot'   : self.memory_info,
            'numcpu'    : self.numcpu_info,
            'featcpu'   : self.featcpu_info,
            'freqcpu'   : self.freqcpu_info,
            'macaddr'   : self.macaddr_info,
            'ipaddr'    : self.ipaddr_info}

    def dumpOCS(self, hostname, entity):
        """
        Return an OCS XML string
        """

	REQUEST = ET.Element('REQUEST')

	DEVICEID = ET.SubElement(REQUEST,'DEVICEID')
	DEVICEID.text = ("%s-%s" % (hostname, time.strftime("%Y-%m-%d-%H-%M-%S"))).strip(' \t\n\r').strip()

	QUERY = ET.SubElement(REQUEST,'QUERY')
	QUERY.text = 'INVENTORY'

	TAG = ET.SubElement(REQUEST,'TAG')
	TAG.text = entity.strip(' \t\n\r').strip()


	###### CONTENT ##############################
	CONTENT = ET.SubElement(REQUEST,'CONTENT')

	##### Access log section ####################
	ACCESSLOG = ET.SubElement(CONTENT,'ACCESSLOG')

	LOGDATE = ET.SubElement(ACCESSLOG,'LOGDATE')
	LOGDATE.text = time.strftime("%Y-%m-%d %H:%M:%S").strip(' \t\n\r').strip()

	USERID = ET.SubElement(ACCESSLOG,'USERID')
	USERID.text = 'N/A'

	###### BIOS SECTION ##########################
	BIOS = ET.SubElement(CONTENT,'BIOS')



	ASSETTAG = ET.SubElement(BIOS,'ASSETTAG')
	ASSETTAG.text = ''

	MMANUFACTURER = ET.SubElement(BIOS,'MMANUFACTURER')
	MMODEL = ET.SubElement(BIOS,'MMODEL')
	MSN = ET.SubElement(BIOS,'MSN')
	SKUNUMBER = ET.SubElement(BIOS,'SKUNUMBER')
	

	BDATE = ET.SubElement(BIOS,'BDATE')
	BDATE.text = self.bios_info['date'].strip(' \t\n\r').strip()

	BMANUFACTURER = ET.SubElement(BIOS,'BMANUFACTURER')
	BMANUFACTURER.text = self.bios_info['vendor'].strip(' \t\n\r').strip()

	BVERSION = ET.SubElement(BIOS,'BVERSION')
	BVERSION.text = self.bios_info['version'].strip(' \t\n\r').strip()

	SMANUFACTURER = ET.SubElement(BIOS,'SMANUFACTURER')
	SMANUFACTURER.text = self.sys_info['manufacturer'].strip(' \t\n\r').strip()

	SMODEL = ET.SubElement(BIOS,'SMODEL')
	SMODEL.text = self.sys_info['product'].strip(' \t\n\r').strip()

	SSN = ET.SubElement(BIOS,'SSN')
	SSN.text = self.sys_info['serial'].strip(' \t\n\r').strip()

	#### HARDWARE SECTION ###############################
	HARDWARE = ET.SubElement(CONTENT,'HARDWARE')

	IPADDR = ET.SubElement(HARDWARE,'IPADDR')
	IPADDR.text = self.ipaddr_info['ip'].strip(' \t\n\r').strip()

	NAME = ET.SubElement(HARDWARE,'NAME')
	NAME.text = hostname.strip(' \t\n\r').strip()

	UUID = ET.SubElement(HARDWARE,'UUID')
	_uuid = self.sys_info['uuid']
	if len(_uuid) == 32:
		UUID.text = _uuid[0:8]+'-'+_uuid[8:12]+'-'+_uuid[12:16]+'-'+_uuid[16:20]+'-'+_uuid[20:32]

	OSNAME = ET.SubElement(HARDWARE,'OSNAME')
	OSNAME.text = 'Unknown operating system (PXE network boot inventory)'

	CHASSIS_TYPE = ET.SubElement(HARDWARE,'CHASSIS_TYPE')
	if self.enclos_info['type'] in COMPUTER_TYPES:
		CHASSIS_TYPE.text = COMPUTER_TYPES[self.enclos_info['type']]
	else:
		CHASSIS_TYPE.text = 'Unknown'

	PROCESSORS = ET.SubElement(HARDWARE,'PROCESSORS')
	PROCESSORS.text = str(int(self.freqcpu_info / 1000))

	PROCESSORN = ET.SubElement(HARDWARE,'PROCESSORN')
	PROCESSORN.text = str(self.numcpu_info)

	PROCESSORT = ET.SubElement(HARDWARE,'PROCESSORT')
	PROCESSORT.text = 'Unknown processor'


	#### NETWORK SECTION ###############################

	NETWORKS = ET.SubElement(CONTENT,'NETWORKS')

	DESCRIPTION = ET.SubElement(NETWORKS,'DESCRIPTION')
	DESCRIPTION.text = 'eth0'

	IPADDRESS = ET.SubElement(NETWORKS,'IPADDRESS')
	IPADDRESS.text = self.ipaddr_info['ip'].strip(' \t\n\r').strip()

	MACADDR = ET.SubElement(NETWORKS,'MACADDR')
	MACADDR.text = self.macaddr_info.strip(' \t\n\r').strip()

	STATUS = ET.SubElement(NETWORKS,'STATUS')
	STATUS.text = 'Up'

	TYPE = ET.SubElement(NETWORKS,'TYPE')
	TYPE.text = 'Ethernet'

	VIRTUALDEV = ET.SubElement(NETWORKS,'VIRTUALDEV')
	VIRTUALDEV.text = '0'


	#### STORAGE SECTION ###################################

	for k,v in self.disk_info.iteritems():
		STORAGES = ET.SubElement(CONTENT,'STORAGES')
		
		NAME = ET.SubElement(STORAGES,'NAME')
		NAME.text = 'hd'+k

		TYPE = ET.SubElement(STORAGES,'TYPE')
		TYPE.text = 'disk'
		
		DISKSIZE = ET.SubElement(STORAGES,'DISKSIZE')
		DISKSIZE.text = str(v['lba_size_mb'])

	# DRIVES SECTION #####################################

	for diskid in self.disk_info.keys():
		for partid,partinfo in self.disk_info[diskid]['parts'].iteritems():
			DRIVES = ET.SubElement(CONTENT,'DRIVES')

			FILESYSTEM = ET.SubElement(DRIVES,'FILESYSTEM')
			if partinfo['type_hex'] in FILESYSTEMS_H:
				FILESYSTEM.text = FILESYSTEMS_H[partinfo['type_hex']]
			
			TOTAL = ET.SubElement(DRIVES,'TOTAL')
			TOTAL.text = str(partinfo['length_mb'])
			
			TYPE = ET.SubElement(DRIVES,'TYPE')
			TYPE.text = 'hd'+diskid+'p'+partid
		
	# MEMORY SECTION #####################################

	for mem_slot in self.memory_info:
			if not mem_slot['size']: continue
			MEMORIES = ET.SubElement(CONTENT,'MEMORIES')

			CAPACITY = ET.SubElement(MEMORIES,'CAPACITY')
			CAPACITY.text = str(mem_slot['size'])

			CAPTION = ET.SubElement(MEMORIES,'CAPTION')
			CAPTION.text = mem_slot['location'].strip(' \t\n\r').strip()

			DESCRIPTION = ET.SubElement(MEMORIES,'DESCRIPTION')
			DESCRIPTION.text = 'Unknown'

			MEMORYCORRECTION = ET.SubElement(MEMORIES,'MEMORYCORRECTION')
			MEMORYCORRECTION.text = 'Unknown'

			NUMSLOTS = ET.SubElement(MEMORIES,'NUMSLOTS')
			NUMSLOTS.text = '1'

			SERIALNUMBER = ET.SubElement(MEMORIES,'SERIALNUMBER')
			SERIALNUMBER.text = 'Unknown'

			TYPE = ET.SubElement(MEMORIES,'TYPE')
			TYPE.text = 'N/A'

			SPEED = ET.SubElement(MEMORIES,'SPEED')
			if mem_slot['speed']:
				SPEED.text = str(mem_slot['speed'])+' MHz'
			else:
				SPEED.text = 'N/A'

	return '<?xml version="1.0" encoding="utf-8"?>'+ET.tostring(REQUEST)
