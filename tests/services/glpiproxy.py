#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2012 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Test module for the scheduler balance module - part of advanced scheduling
"""

import unittest

from pulse2.inventoryserver.glpiproxy import GlpiProxy
from pulse2.inventoryserver.glpiproxy import _ErrorHandler, FusionErrorHandler


class class01ErrorHandler(unittest.TestCase):
    """ Test of error handling on parsing XML responses"""

    def test01issubclass(self):
        result = issubclass(FusionErrorHandler, _ErrorHandler)
        self.assertEqual(result, True)

    def test02parse_correct_response(self):
        message = ok_response()
        result = FusionErrorHandler(message)

        nbr_errors = len(result)
         
        self.assertEqual(nbr_errors, 0)

    def test03parse_incorrect_response(self):
        message = not_ok_response()
        result = FusionErrorHandler(message)

        nbr_errors = len(result)
         
        self.assertNotEqual(nbr_errors, 0)

        

class class02GlpiProxyTest(unittest.TestCase):
    """ Test of forwarding inventories to GLPI """
    def setUp (self):
        self.xml_content = xml_inventory()
        self.url = "http://192.168.127.194/glpi/plugins/fusioninventory/front/plugin_fusioninventory.communication.php"

    def test01post_correct_xml(self):
        glpi_proxy = GlpiProxy(self.url)
        glpi_proxy.send(self.xml_content)
        result = glpi_proxy.result

        nbr_errors = len(result)
         
        self.assertEqual(nbr_errors, 0)

    def test02post_incorrect_xml(self):
        glpi_proxy = GlpiProxy(self.url)
        glpi_proxy.send(self.xml_content + "abcd*-/" )
        result = glpi_proxy.result

        nbr_errors = len(result)
         
        self.assertNotEqual(nbr_errors, 0)


def ok_response():
    return """<?xml version="1.0" encoding="UTF-8"?>
<REPLY><RESPONSE>no_update</RESPONSE></REPLY>
"""

def not_ok_response():
    return """<?xml version="1.0" encoding="UTF-8"?>
<REPLY>
     <ERROR>XML not well formed!</ERROR>
</REPLY>"""



def xml_inventory() : 
    return """<?xml version="1.0" encoding="UTF-8" ?>
<REQUEST>
  <CONTENT>
    <ACCESSLOG>
      <LOGDATE>2012-11-26 23:41:08</LOGDATE>
    </ACCESSLOG>
    <BIOS>
      <ASSETTAG />  <BDATE>01/01/2007</BDATE>
      <BMANUFACTURER>Bochs</BMANUFACTURER>
      <BVERSION>Bochs</BVERSION>
      <MMANUFACTURER />  <MMODEL />  <MSN />  <SKUNUMBER />  <SMANUFACTURER>Bochs</SMANUFACTURER>
      <SMODEL>Bochs</SMODEL>
      <SSN /></BIOS>
    <CONTROLLERS>
      <CAPTION>82371AB/EB/MB PIIX4 ACPI</CAPTION>
      <DRIVER>piix4_smbus</DRIVER>
      <MANUFACTURER>Intel Corporation</MANUFACTURER>
      <NAME>82371AB/EB/MB PIIX4 ACPI</NAME>
      <PCICLASS>0680</PCICLASS>
      <PCIID>8086:7113</PCIID>
      <PCISLOT>00:01.3</PCISLOT>
      <REV>03</REV>
      <TYPE>Bridge</TYPE>
    </CONTROLLERS>
    <CONTROLLERS>
      <CAPTION>GD 5446</CAPTION>
      <MANUFACTURER>Cirrus Logic</MANUFACTURER>
      <NAME>GD 5446</NAME>
      <PCICLASS>0300</PCICLASS>
      <PCIID>1013:00b8</PCIID>
      <PCISLOT>00:02.0</PCISLOT>
      <TYPE>VGA compatible controller</TYPE>
    </CONTROLLERS>
    <CONTROLLERS>
      <CAPTION>82540EM Gigabit Ethernet Controller</CAPTION>
      <DRIVER>e1000</DRIVER>
      <MANUFACTURER>Intel Corporation</MANUFACTURER>
      <NAME>82540EM Gigabit Ethernet Controller</NAME>
      <PCICLASS>0200</PCICLASS>
      <PCIID>8086:100e</PCIID>
      <PCISLOT>00:03.0</PCISLOT>
      <REV>03</REV>
      <TYPE>Ethernet controller</TYPE>
    </CONTROLLERS>
    <CONTROLLERS>
      <CAPTION>82801FB/FBM/FR/FW/FRW (ICH6 Family) High Definition Audio Controller</CAPTION>
      <DRIVER>HDA</DRIVER>
      <MANUFACTURER>Intel Corporation</MANUFACTURER>
      <NAME>82801FB/FBM/FR/FW/FRW (ICH6 Family) High Definition Audio Controller</NAME>
      <PCICLASS>0403</PCICLASS>
      <PCIID>8086:2668</PCIID>
      <PCISLOT>00:04.0</PCISLOT>
      <REV>01</REV>
      <TYPE>Audio device</TYPE>
    </CONTROLLERS>
    <CONTROLLERS>
      <CAPTION>Virtio block device</CAPTION>
      <DRIVER>virtio</DRIVER>
      <MANUFACTURER>Red Hat, Inc</MANUFACTURER>
      <NAME>Virtio block device</NAME>
      <PCICLASS>0100</PCICLASS>
      <PCIID>1af4:1001</PCIID>
      <PCISLOT>00:05.0</PCISLOT>
      <TYPE>SCSI storage controller</TYPE>
    </CONTROLLERS>
    <CONTROLLERS>
      <CAPTION>Virtio memory balloon</CAPTION>
      <DRIVER>virtio</DRIVER>
      <MANUFACTURER>Red Hat, Inc</MANUFACTURER>
      <NAME>Virtio memory balloon</NAME>
      <PCICLASS>0500</PCICLASS>
      <PCIID>1af4:1002</PCIID>
      <PCISLOT>00:06.0</PCISLOT>
      <TYPE>RAM memory</TYPE>
    </CONTROLLERS>
    <CPUS>
      <CORE>1</CORE>
      <FAMILYNAME>Other</FAMILYNAME>
      <FAMILYNUMBER>6</FAMILYNUMBER>
      <ID>33 06 00 00 FD AB 81 07</ID>
      <MANUFACTURER>Intel</MANUFACTURER>
      <MODEL>3</MODEL>
      <NAME>QEMU Virtual CPU version 1.1.1</NAME>
      <SPEED>2000</SPEED>
      <STEPPING>3</STEPPING>
      <THREAD>1</THREAD>
    </CPUS>
    <DRIVES>
      <FILESYSTEM>ext3</FILESYSTEM>
      <FREE>5871</FREE>
      <SERIAL>afda500a-8a38-485a-b67c-6bffe5be8829</SERIAL>
      <TOTAL>7502</TOTAL>
      <TYPE>/</TYPE>
      <VOLUMN>/dev/vda1</VOLUMN>
    </DRIVES>
    <ENVS>
      <KEY>VERBOSE</KEY>
      <VAL>no</VAL>
    </ENVS>
    <ENVS>
      <KEY>HOME</KEY>
      <VAL>/</VAL>
    </ENVS>
    <ENVS>
      <KEY>CONSOLE</KEY>
      <VAL>/dev/console</VAL>
    </ENVS>
    <ENVS>
      <KEY>PREVLEVEL</KEY>
      <VAL>N</VAL>
    </ENVS>
    <ENVS>
      <KEY>LC_ALL</KEY>
      <VAL>C</VAL>
    </ENVS>
    <ENVS>
      <KEY>RUNLEVEL</KEY>
      <VAL>2</VAL>
    </ENVS>
    <ENVS>
      <KEY>init</KEY>
      <VAL>/sbin/init</VAL>
    </ENVS>
    <ENVS>
      <KEY>previous</KEY>
      <VAL>N</VAL>
    </ENVS>
    <ENVS>
      <KEY>LINES</KEY>
      <VAL>25</VAL>
    </ENVS>
    <ENVS>
      <KEY>COLUMNS</KEY>
      <VAL>80</VAL>
    </ENVS>
    <ENVS>
      <KEY>PWD</KEY>
      <VAL>/</VAL>
    </ENVS>
    <ENVS>
      <KEY>LANG</KEY>
      <VAL>C</VAL>
    </ENVS>
    <ENVS>
      <KEY>runlevel</KEY>
      <VAL>2</VAL>
    </ENVS>
    <ENVS>
      <KEY>INIT_VERSION</KEY>
      <VAL>sysvinit-2.88</VAL>
    </ENVS>
    <ENVS>
      <KEY>PATH</KEY>
      <VAL>/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin</VAL>
    </ENVS>
    <ENVS>
      <KEY>rootmnt</KEY>
      <VAL>/root</VAL>
    </ENVS>
    <ENVS>
      <KEY>BOOT_IMAGE</KEY>
      <VAL>/boot/vmlinuz-2.6.32-5-686</VAL>
    </ENVS>
    <ENVS>
      <KEY>SHELL</KEY>
      <VAL>/bin/sh</VAL>
    </ENVS>
    <ENVS>
      <KEY>TERM</KEY>
      <VAL>linux</VAL>
    </ENVS>
    <HARDWARE>
      <ARCHNAME>i486-linux-gnu-thread-multi</ARCHNAME>
      <CHASSIS_TYPE>Other</CHASSIS_TYPE>
      <CHECKSUM>1</CHECKSUM>
      <DATELASTLOGGEDUSER>Mon Nov 26 15:02</DATELASTLOGGEDUSER>
      <DEFAULTGATEWAY>192.168.127.1</DEFAULTGATEWAY>
      <DESCRIPTION>i686/00-00-00 08:38:51</DESCRIPTION>
      <DNS>192.168.127.1</DNS>
      <ETIME>0</ETIME>
      <IPADDR>192.168.127.4</IPADDR>
      <LASTLOGGEDUSER>root</LASTLOGGEDUSER>
      <MEMORY>375</MEMORY>
      <NAME>debian-squeeze</NAME>
      <OSCOMMENTS>#1 SMP Sun May 6 04:01:19 UTC 2012</OSCOMMENTS>
      <OSNAME>Debian GNU/Linux 6.0.5</OSNAME>
      <OSVERSION>2.6.32-5-686</OSVERSION>
      <PROCESSORN>1</PROCESSORN>
      <PROCESSORS>2000</PROCESSORS>
      <PROCESSORT>QEMU Virtual CPU version 1.1.1</PROCESSORT>
      <SWAP>374</SWAP>
      <USERDOMAIN />  <USERID>root</USERID>
      <UUID>B7666729-927F-CA23-38FE-549A9E6933AA</UUID>
      <VMSYSTEM>QEMU</VMSYSTEM>
      <WINPRODID />  <WORKGROUP></WORKGROUP>
    </HARDWARE>
    <INPUTS>
      <CAPTION>AT Translated Set 2 keyboard</CAPTION>
      <DESCRIPTION>AT Translated Set 2 keyboard</DESCRIPTION>
      <TYPE>Keyboard</TYPE>
    </INPUTS>
    <INPUTS>
      <CAPTION>PC Speaker</CAPTION>
      <DESCRIPTION>PC Speaker</DESCRIPTION>
      <TYPE>Keyboard</TYPE>
    </INPUTS>
    <INPUTS>
      <CAPTION>QEMU 1.1.1 QEMU USB Tablet</CAPTION>
      <DESCRIPTION>QEMU 1.1.1 QEMU USB Tablet</DESCRIPTION>
      <TYPE>Pointing</TYPE>
    </INPUTS>
    <INPUTS>
      <CAPTION>ImExPS/2 Generic Explorer Mouse</CAPTION>
      <DESCRIPTION>ImExPS/2 Generic Explorer Mouse</DESCRIPTION>
      <TYPE>Pointing</TYPE>
    </INPUTS>
    <MEMORIES>
      <CAPACITY>384</CAPACITY>
      <CAPTION>DIMM 0</CAPTION>
      <DESCRIPTION>DIMM (Multi-bit ECC)</DESCRIPTION>
      <MEMORYCORRECTION>Multi-bit ECC</MEMORYCORRECTION>
      <NUMSLOTS>1</NUMSLOTS>
      <TYPE>RAM</TYPE>
    </MEMORIES>
    <MONITORS />
    <NETWORKS>
      <DESCRIPTION>lo</DESCRIPTION>
      <IPADDRESS>127.0.0.1</IPADDRESS>
      <IPMASK>255.0.0.0</IPMASK>
      <IPSUBNET>127.0.0.0</IPSUBNET>
      <MACADDR>00:00:00:00:00:00</MACADDR>
      <SLAVES></SLAVES>
      <STATUS>Up</STATUS>
      <VIRTUALDEV>1</VIRTUALDEV>
    </NETWORKS>
    <NETWORKS>
      <DESCRIPTION>lo</DESCRIPTION>
      <IPADDRESS6>::1</IPADDRESS6>
      <IPMASK6>fff0::</IPMASK6>
      <IPSUBNET6>::</IPSUBNET6>
      <MACADDR>00:00:00:00:00:00</MACADDR>
      <SLAVES></SLAVES>
      <STATUS>Up</STATUS>
      <VIRTUALDEV>1</VIRTUALDEV>
    </NETWORKS>
    <NETWORKS>
      <DESCRIPTION>eth0</DESCRIPTION>
      <DRIVER>e1000</DRIVER>
      <IPADDRESS>192.168.127.23</IPADDRESS>
      <IPMASK>255.255.255.0</IPMASK>
      <IPSUBNET>192.168.127.0</IPSUBNET>
      <MACADDR>52:54:00:23:23:23</MACADDR>
      <PCISLOT>0000:00:03.0</PCISLOT>
      <SLAVES></SLAVES>
      <STATUS>Up</STATUS>
      <VIRTUALDEV>0</VIRTUALDEV>
    </NETWORKS>
    <NETWORKS>
      <DESCRIPTION>eth0</DESCRIPTION>
      <DRIVER>e1000</DRIVER>
      <IPADDRESS6>fe80::5054:ff:fe65:d649</IPADDRESS6>
      <IPMASK6>ffff:ffff:ffff:ffff::</IPMASK6>
      <IPSUBNET6>fe80::</IPSUBNET6>
      <MACADDR>52:54:00:65:d6:49</MACADDR>
      <PCISLOT>0000:00:03.0</PCISLOT>
      <SLAVES></SLAVES>
      <STATUS>Up</STATUS>
      <VIRTUALDEV>0</VIRTUALDEV>
    </NETWORKS>
    <OPERATINGSYSTEM>
      <FULL_NAME>Debian GNU/Linux 6.0.5</FULL_NAME>
      <KERNEL_NAME>linux</KERNEL_NAME>
      <KERNEL_VERSION>2.6.32-5-686</KERNEL_VERSION>
      <NAME>Debian</NAME>
      <VERSION>6.0.5</VERSION>
    </OPERATINGSYSTEM>
    <PROCESSES>
      <CMD>init [2]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>2036</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kthreadd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>2</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[migration/0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>3</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[ksoftirqd/0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>4</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[watchdog/0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>5</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[events/0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>6</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[cpuset]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>7</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[khelper]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>8</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[netns]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>9</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[async/mgr]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>10</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[pm]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>11</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[sync_supers]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>12</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[bdi-default]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>13</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kintegrityd/0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>14</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kblockd/0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>15</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kacpid]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>16</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kacpi_notify]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>17</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kacpi_hotplug]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>18</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kseriod]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>19</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kondemand/0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>21</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[khungtaskd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>22</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kswapd0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>23</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[ksmd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>24</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[aio/0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>25</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[crypto/0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>26</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[ksuspend_usbd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>186</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[khubd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>187</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[ata/0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>189</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[ata_aux]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>190</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[scsi_eh_0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>195</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[scsi_eh_1]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>198</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kjournald]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>224</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>udevd --daemon</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.2</MEM>
      <PID>294</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>2504</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>udevd --daemon</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.2</MEM>
      <PID>413</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>2388</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>udevd --daemon</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>414</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>2388</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[vballoon]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>461</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kpsmoused]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>474</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[hd-audio0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>492</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[usbhid_resume]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>502</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[flush-254:0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>539</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/sbin/portmap</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>736</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>daemon</USER>
      <VIRTUALMEMORY>1812</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/sbin/rpc.statd</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.2</MEM>
      <PID>749</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>statd</USER>
      <VIRTUALMEMORY>1940</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[rpciod/0]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>752</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kslowd000]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>754</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[kslowd001]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>755</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[nfsiod]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>756</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/rpc.i</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>762</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>2276</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/rsysl</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.3</MEM>
      <PID>904</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>27452</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[lockd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>931</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[nfsd4]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>933</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[nfsd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>934</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[nfsd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>936</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[nfsd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>937</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[nfsd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>939</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[nfsd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>940</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[nfsd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>942</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[nfsd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>944</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>[nfsd]</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>945</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>0</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/rpc.m</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.0</MEM>
      <PID>954</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>2112</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/acpid</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>974</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1708</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/apach</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>1.8</MEM>
      <PID>989</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>24020</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/apach</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.9</MEM>
      <PID>1001</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>www-data</USER>
      <VIRTUALMEMORY>24020</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/apach</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.9</MEM>
      <PID>1002</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>www-data</USER>
      <VIRTUALMEMORY>24020</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/apach</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.9</MEM>
      <PID>1003</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>www-data</USER>
      <VIRTUALMEMORY>24020</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/apach</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.9</MEM>
      <PID>1004</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>www-data</USER>
      <VIRTUALMEMORY>24020</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/apach</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.9</MEM>
      <PID>1005</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>www-data</USER>
      <VIRTUALMEMORY>24020</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/bin/perl /</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>5.2</MEM>
      <PID>1009</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>30084</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/bin/sh /usr/bi</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1036</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1752</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/mysql</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>5.7</MEM>
      <PID>1147</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>mysql</USER>
      <VIRTUALMEMORY>139468</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>logger -t mysql</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1148</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1676</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/inetd</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1179</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1880</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/slapd</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>1.1</MEM>
      <PID>1185</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>openldap</USER>
      <VIRTUALMEMORY>33100</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/cron</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.2</MEM>
      <PID>1225</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>3816</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/pulse</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1277</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1732</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>python /usr/sbi</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>7.2</MEM>
      <PID>1296</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>42472</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/bin/python</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>3.1</MEM>
      <PID>1318</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>14948</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>dhclient -v -pf</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.2</MEM>
      <PID>1334</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>2336</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>ssh-agent</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1353</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>3240</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/sbin/sshd</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.2</MEM>
      <PID>1372</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>5500</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/bin/python</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>4.4</MEM>
      <PID>1378</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>30960</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/bin/python</CMD>
      <CPUUSAGE>0.1</CPUUSAGE>
      <MEM>5.1</MEM>
      <PID>1462</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>40360</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/bin/python</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>3.1</MEM>
      <PID>1496</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>24608</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/sbin/getty 384</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1510</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>tty1</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1712</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/sbin/getty 384</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1511</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>tty2</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1712</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/sbin/getty 384</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1512</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>tty3</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1712</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/sbin/getty 384</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1513</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>tty4</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1712</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/sbin/getty 384</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1514</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>tty5</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1712</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/sbin/getty 384</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>1515</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>tty6</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1712</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>sshd: root@pts/</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.7</MEM>
      <PID>1516</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>8264</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>-bash</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.4</MEM>
      <PID>1518</PID>
      <STARTED>2012-11-26 15:02</STARTED>
      <TTY>pts/0</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>4508</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>/usr/bin/perl /</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>7.0</MEM>
      <PID>3041</PID>
      <STARTED>2012-11-26 23:41</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>37532</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>sh -c ps aux 2&gt;</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.1</MEM>
      <PID>3048</PID>
      <STARTED>2012-11-26 23:41</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>1752</VIRTUALMEMORY>
    </PROCESSES>
    <PROCESSES>
      <CMD>ps aux</CMD>
      <CPUUSAGE>0.0</CPUUSAGE>
      <MEM>0.2</MEM>
      <PID>3049</PID>
      <STARTED>2012-11-26 23:41</STARTED>
      <TTY>?</TTY>
      <USER>root</USER>
      <VIRTUALMEMORY>2356</VIRTUALMEMORY>
    </PROCESSES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>displays information on ACPI devices</COMMENTS>
      <FILESIZE>88</FILESIZE>
      <FROM>deb</FROM>
      <NAME>acpi</NAME>
      <VERSION>1.5-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>scripts for handling base ACPI events such as the power button</COMMENTS>
      <FILESIZE>84</FILESIZE>
      <FROM>deb</FROM>
      <NAME>acpi-support-base</NAME>
      <VERSION>0.137-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Advanced Configuration and Power Interface event daemon</COMMENTS>
      <FILESIZE>200</FILESIZE>
      <FROM>deb</FROM>
      <NAME>acpid</NAME>
      <VERSION>1:2.0.7-1squeeze4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>add and remove users and groups</COMMENTS>
      <FILESIZE>1228</FILESIZE>
      <FROM>deb</FROM>
      <NAME>adduser</NAME>
      <VERSION>3.112+nmu2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Apache HTTP Server - traditional non-threaded model</COMMENTS>
      <FILESIZE>68</FILESIZE>
      <FROM>deb</FROM>
      <NAME>apache2-mpm-prefork</NAME>
      <VERSION>2.2.16-6+squeeze7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>utility programs for webservers</COMMENTS>
      <FILESIZE>372</FILESIZE>
      <FROM>deb</FROM>
      <NAME>apache2-utils</NAME>
      <VERSION>2.2.16-6+squeeze7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Apache HTTP Server common binary files</COMMENTS>
      <FILESIZE>3392</FILESIZE>
      <FROM>deb</FROM>
      <NAME>apache2.2-bin</NAME>
      <VERSION>2.2.16-6+squeeze7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Apache HTTP Server common files</COMMENTS>
      <FILESIZE>2144</FILESIZE>
      <FROM>deb</FROM>
      <NAME>apache2.2-common</NAME>
      <VERSION>2.2.16-6+squeeze7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Advanced front-end for dpkg</COMMENTS>
      <FILESIZE>6116</FILESIZE>
      <FROM>deb</FROM>
      <NAME>apt</NAME>
      <VERSION>0.8.10.3+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>APT utility programs</COMMENTS>
      <FILESIZE>592</FILESIZE>
      <FROM>deb</FROM>
      <NAME>apt-utils</NAME>
      <VERSION>0.8.10.3+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>terminal-based package manager (terminal interface only)</COMMENTS>
      <FILESIZE>11720</FILESIZE>
      <FROM>deb</FROM>
      <NAME>aptitude</NAME>
      <VERSION>0.6.3-3.2+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>advanced TFTP server</COMMENTS>
      <FILESIZE>224</FILESIZE>
      <FROM>deb</FROM>
      <NAME>atftpd</NAME>
      <VERSION>0.7.dfsg-9.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>automatic configure script builder</COMMENTS>
      <FILESIZE>2256</FILESIZE>
      <FROM>deb</FROM>
      <NAME>autoconf</NAME>
      <VERSION>2.67-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>A tool for generating GNU Standards-compliant Makefiles</COMMENTS>
      <FILESIZE>1812</FILESIZE>
      <FROM>deb</FROM>
      <NAME>automake</NAME>
      <VERSION>1:1.11.1-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>The autopoint program from GNU gettext</COMMENTS>
      <FILESIZE>684</FILESIZE>
      <FROM>deb</FROM>
      <NAME>autopoint</NAME>
      <VERSION>0.18.1.1-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Update infrastructure for config.{guess,sub} files</COMMENTS>
      <FILESIZE>216</FILESIZE>
      <FROM>deb</FROM>
      <NAME>autotools-dev</NAME>
      <VERSION>20100122.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Debian base system miscellaneous files</COMMENTS>
      <FILESIZE>472</FILESIZE>
      <FROM>deb</FROM>
      <NAME>base-files</NAME>
      <VERSION>6.0squeeze5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Debian base system master password and group files</COMMENTS>
      <FILESIZE>180</FILESIZE>
      <FROM>deb</FROM>
      <NAME>base-passwd</NAME>
      <VERSION>3.5.22</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU Bourne Again SHell</COMMENTS>
      <FILESIZE>3480</FILESIZE>
      <FROM>deb</FROM>
      <NAME>bash</NAME>
      <VERSION>4.1-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU assembler, linker and binary utilities</COMMENTS>
      <FILESIZE>10944</FILESIZE>
      <FROM>deb</FROM>
      <NAME>binutils</NAME>
      <VERSION>2.20.1-16</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>collection of more utilities from FreeBSD</COMMENTS>
      <FILESIZE>728</FILESIZE>
      <FROM>deb</FROM>
      <NAME>bsdmainutils</NAME>
      <VERSION>8.0.13</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Basic utilities from 4.4BSD-Lite</COMMENTS>
      <FILESIZE>196</FILESIZE>
      <FROM>deb</FROM>
      <NAME>bsdutils</NAME>
      <VERSION>1:2.17.2-9</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Informational list of build-essential packages</COMMENTS>
      <FILESIZE>48</FILESIZE>
      <FROM>deb</FROM>
      <NAME>build-essential</NAME>
      <VERSION>11.5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Tiny utilities for small and embedded systems</COMMENTS>
      <FILESIZE>480</FILESIZE>
      <FROM>deb</FROM>
      <NAME>busybox</NAME>
      <VERSION>1:1.17.1-8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>high-quality block-sorting file compressor - utilities</COMMENTS>
      <FILESIZE>156</FILESIZE>
      <FROM>deb</FROM>
      <NAME>bzip2</NAME>
      <VERSION>1.0.5-6+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Common CA certificates</COMMENTS>
      <FILESIZE>652</FILESIZE>
      <FROM>deb</FROM>
      <NAME>ca-certificates</NAME>
      <VERSION>20090814+nmu3squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>console font and keymap setup program</COMMENTS>
      <FILESIZE>1512</FILESIZE>
      <FROM>deb</FROM>
      <NAME>console-setup</NAME>
      <VERSION>1.68+squeeze2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Fixed-width fonts for fast reading on the Linux console</COMMENTS>
      <FILESIZE>776</FILESIZE>
      <FROM>deb</FROM>
      <NAME>console-terminus</NAME>
      <VERSION>4.30-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU core utilities</COMMENTS>
      <FILESIZE>12188</FILESIZE>
      <FROM>deb</FROM>
      <NAME>coreutils</NAME>
      <VERSION>8.5-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU cpio -- a program to manage archives of files</COMMENTS>
      <FILESIZE>892</FILESIZE>
      <FROM>deb</FROM>
      <NAME>cpio</NAME>
      <VERSION>2.11-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU C preprocessor (cpp)</COMMENTS>
      <FILESIZE>76</FILESIZE>
      <FROM>deb</FROM>
      <NAME>cpp</NAME>
      <VERSION>4:4.4.5-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU C preprocessor</COMMENTS>
      <FILESIZE>8456</FILESIZE>
      <FROM>deb</FROM>
      <NAME>cpp-4.4</NAME>
      <VERSION>4.4.5-8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>process scheduling daemon</COMMENTS>
      <FILESIZE>336</FILESIZE>
      <FROM>deb</FROM>
      <NAME>cron</NAME>
      <VERSION>3.0pl1-116</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>POSIX-compliant shell</COMMENTS>
      <FILESIZE>228</FILESIZE>
      <FROM>deb</FROM>
      <NAME>dash</NAME>
      <VERSION>0.5.5.1-7.4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Debian configuration management system</COMMENTS>
      <FILESIZE>1032</FILESIZE>
      <FROM>deb</FROM>
      <NAME>debconf</NAME>
      <VERSION>1.5.36.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>full internationalization support for debconf</COMMENTS>
      <FILESIZE>1208</FILESIZE>
      <FROM>deb</FROM>
      <NAME>debconf-i18n</NAME>
      <VERSION>1.5.36.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>GnuPG archive keys of the Debian archive</COMMENTS>
      <FILESIZE>64</FILESIZE>
      <FROM>deb</FROM>
      <NAME>debian-archive-keyring</NAME>
      <VERSION>2010.08.28</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Miscellaneous utilities specific to Debian</COMMENTS>
      <FILESIZE>216</FILESIZE>
      <FROM>deb</FROM>
      <NAME>debianutils</NAME>
      <VERSION>3.4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>File comparison utilities</COMMENTS>
      <FILESIZE>1320</FILESIZE>
      <FROM>deb</FROM>
      <NAME>diffutils</NAME>
      <VERSION>1:3.0-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>hardware identification system</COMMENTS>
      <FILESIZE>172</FILESIZE>
      <FROM>deb</FROM>
      <NAME>discover</NAME>
      <VERSION>2.1.2-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Data lists for Discover hardware detection system</COMMENTS>
      <FILESIZE>3820</FILESIZE>
      <FROM>deb</FROM>
      <NAME>discover-data</NAME>
      <VERSION>2.2010.10.18</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Dump Desktop Management Interface data</COMMENTS>
      <FILESIZE>168</FILESIZE>
      <FROM>deb</FROM>
      <NAME>dmidecode</NAME>
      <VERSION>2.9-1.2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The Linux Kernel Device Mapper userspace library</COMMENTS>
      <FILESIZE>184</FILESIZE>
      <FROM>deb</FROM>
      <NAME>dmsetup</NAME>
      <VERSION>2:1.02.48-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>standard XML documentation system for software and systems</COMMENTS>
      <FILESIZE>2488</FILESIZE>
      <FROM>deb</FROM>
      <NAME>docbook-xml</NAME>
      <VERSION>4.5-7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>stylesheets for processing DocBook XML to various output formats</COMMENTS>
      <FILESIZE>12792</FILESIZE>
      <FROM>deb</FROM>
      <NAME>docbook-xsl</NAME>
      <VERSION>1.75.2+dfsg-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>stylesheets for processing DocBook XML files (HTML documentation)</COMMENTS>
      <FILESIZE>5784</FILESIZE>
      <FROM>deb</FROM>
      <NAME>docbook-xsl-doc-html</NAME>
      <VERSION>1.75.2-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Debian package management system</COMMENTS>
      <FILESIZE>6868</FILESIZE>
      <FROM>deb</FROM>
      <NAME>dpkg</NAME>
      <VERSION>1.15.8.12</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Debian package development tools</COMMENTS>
      <FILESIZE>1440</FILESIZE>
      <FROM>deb</FROM>
      <NAME>dpkg-dev</NAME>
      <VERSION>1.15.8.12</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>ext2/ext3/ext4 file system libraries</COMMENTS>
      <FILESIZE>300</FILESIZE>
      <FROM>deb</FROM>
      <NAME>e2fslibs</NAME>
      <VERSION>1.41.12-4stable1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>ext2/ext3/ext4 file system utilities</COMMENTS>
      <FILESIZE>2032</FILESIZE>
      <FROM>deb</FROM>
      <NAME>e2fsprogs</NAME>
      <VERSION>1.41.12-4stable1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>ejects CDs and operates CD-Changers under Linux</COMMENTS>
      <FILESIZE>336</FILESIZE>
      <FROM>deb</FROM>
      <NAME>eject</NAME>
      <VERSION>2.1.5+deb1+cvs20081104-7.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Gives a fake root environment</COMMENTS>
      <FILESIZE>440</FILESIZE>
      <FROM>deb</FROM>
      <NAME>fakeroot</NAME>
      <VERSION>1.14.4-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Determines file type using &quot;magic&quot; numbers</COMMENTS>
      <FILESIZE>136</FILESIZE>
      <FROM>deb</FROM>
      <NAME>file</NAME>
      <VERSION>5.04-5+squeeze2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>utilities for finding files--find, xargs</COMMENTS>
      <FILESIZE>1704</FILESIZE>
      <FROM>deb</FROM>
      <NAME>findutils</NAME>
      <VERSION>4.4.2-1+b1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>generic font configuration library - configuration</COMMENTS>
      <FILESIZE>440</FILESIZE>
      <FROM>deb</FROM>
      <NAME>fontconfig-config</NAME>
      <VERSION>2.8.0-2.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Hardware and software inventory tool (client)</COMMENTS>
      <FILESIZE>1540</FILESIZE>
      <FROM>deb</FROM>
      <NAME>fusioninventory-agent</NAME>
      <VERSION>2.2.3-2~bpo60+2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU C++ compiler</COMMENTS>
      <FILESIZE>40</FILESIZE>
      <FROM>deb</FROM>
      <NAME>g++</NAME>
      <VERSION>4:4.4.5-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU C++ compiler</COMMENTS>
      <FILESIZE>10496</FILESIZE>
      <FROM>deb</FROM>
      <NAME>g++-4.4</NAME>
      <VERSION>4.4.5-8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU C compiler</COMMENTS>
      <FILESIZE>64</FILESIZE>
      <FROM>deb</FROM>
      <NAME>gcc</NAME>
      <VERSION>4:4.4.5-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU C compiler</COMMENTS>
      <FILESIZE>4572</FILESIZE>
      <FROM>deb</FROM>
      <NAME>gcc-4.4</NAME>
      <VERSION>4.4.5-8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU Compiler Collection (base package)</COMMENTS>
      <FILESIZE>176</FILESIZE>
      <FROM>deb</FROM>
      <NAME>gcc-4.4-base</NAME>
      <VERSION>4.4.5-8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU Internationalization utilities</COMMENTS>
      <FILESIZE>6844</FILESIZE>
      <FROM>deb</FROM>
      <NAME>gettext</NAME>
      <VERSION>0.18.1.1-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU Internationalization utilities for the base system</COMMENTS>
      <FILESIZE>1000</FILESIZE>
      <FROM>deb</FROM>
      <NAME>gettext-base</NAME>
      <VERSION>0.18.1.1-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>fast, scalable, distributed revision control system</COMMENTS>
      <FILESIZE>9940</FILESIZE>
      <FROM>deb</FROM>
      <NAME>git</NAME>
      <VERSION>1:1.7.2.5-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU privacy guard - a free PGP replacement</COMMENTS>
      <FILESIZE>5176</FILESIZE>
      <FROM>deb</FROM>
      <NAME>gnupg</NAME>
      <VERSION>1.4.10-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU privacy guard - signature verification tool</COMMENTS>
      <FILESIZE>396</FILESIZE>
      <FROM>deb</FROM>
      <NAME>gpgv</NAME>
      <VERSION>1.4.10-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU grep, egrep and fgrep</COMMENTS>
      <FILESIZE>1116</FILESIZE>
      <FROM>deb</FROM>
      <NAME>grep</NAME>
      <VERSION>2.6.3-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU troff text-formatting system (base system components)</COMMENTS>
      <FILESIZE>3320</FILESIZE>
      <FROM>deb</FROM>
      <NAME>groff-base</NAME>
      <VERSION>1.20.1-10</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GRand Unified Bootloader, version 2 (common files)</COMMENTS>
      <FILESIZE>4056</FILESIZE>
      <FROM>deb</FROM>
      <NAME>grub-common</NAME>
      <VERSION>1.98+20100804-14+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GRand Unified Bootloader, version 2 (PC/BIOS version)</COMMENTS>
      <FILESIZE>2560</FILESIZE>
      <FROM>deb</FROM>
      <NAME>grub-pc</NAME>
      <VERSION>1.98+20100804-14+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU compression utilities</COMMENTS>
      <FILESIZE>276</FILESIZE>
      <FROM>deb</FROM>
      <NAME>gzip</NAME>
      <VERSION>1.3.12-9</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>tune hard disk parameters for high performance</COMMENTS>
      <FILESIZE>300</FILESIZE>
      <FROM>deb</FROM>
      <NAME>hdparm</NAME>
      <VERSION>9.32-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>feature-rich BSD mail(1)</COMMENTS>
      <FILESIZE>692</FILESIZE>
      <FROM>deb</FROM>
      <NAME>heirloom-mailx</NAME>
      <VERSION>12.4-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>utility to set/show the host name or domain name</COMMENTS>
      <FILESIZE>84</FILESIZE>
      <FROM>deb</FROM>
      <NAME>hostname</NAME>
      <VERSION>3.04</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>high level tools to configure network interfaces</COMMENTS>
      <FILESIZE>224</FILESIZE>
      <FROM>deb</FROM>
      <NAME>ifupdown</NAME>
      <VERSION>0.6.10</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Standalone GNU Info documentation browser</COMMENTS>
      <FILESIZE>392</FILESIZE>
      <FROM>deb</FROM>
      <NAME>info</NAME>
      <VERSION>4.13a.dfsg.1-6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>tools for generating an initramfs</COMMENTS>
      <FILESIZE>468</FILESIZE>
      <FROM>deb</FROM>
      <NAME>initramfs-tools</NAME>
      <VERSION>0.98.8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>scripts for initializing and shutting down the system</COMMENTS>
      <FILESIZE>396</FILESIZE>
      <FROM>deb</FROM>
      <NAME>initscripts</NAME>
      <VERSION>2.88dsf-13.1+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Tool to organize boot sequence using LSB init.d script dependencies</COMMENTS>
      <FILESIZE>292</FILESIZE>
      <FROM>deb</FROM>
      <NAME>insserv</NAME>
      <VERSION>1.14.0-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Manage installed documentation in info format</COMMENTS>
      <FILESIZE>256</FILESIZE>
      <FROM>deb</FROM>
      <NAME>install-info</NAME>
      <VERSION>4.13a.dfsg.1-6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>system installation report</COMMENTS>
      <FILESIZE>108</FILESIZE>
      <FROM>deb</FROM>
      <NAME>installation-report</NAME>
      <VERSION>2.44</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>networking and traffic control tools</COMMENTS>
      <FILESIZE>976</FILESIZE>
      <FROM>deb</FROM>
      <NAME>iproute</NAME>
      <VERSION>20100519-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>administration tools for packet filtering and NAT</COMMENTS>
      <FILESIZE>1120</FILESIZE>
      <FROM>deb</FROM>
      <NAME>iptables</NAME>
      <VERSION>1.4.8-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Tools to test the reachability of network hosts</COMMENTS>
      <FILESIZE>128</FILESIZE>
      <FROM>deb</FROM>
      <NAME>iputils-ping</NAME>
      <VERSION>3:20100418-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>ISC DHCP client</COMMENTS>
      <FILESIZE>628</FILESIZE>
      <FROM>deb</FROM>
      <NAME>isc-dhcp-client</NAME>
      <VERSION>4.1.1-P1-15+squeeze6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>common files used by all the isc-dhcp* packages</COMMENTS>
      <FILESIZE>600</FILESIZE>
      <FROM>deb</FROM>
      <NAME>isc-dhcp-common</NAME>
      <VERSION>4.1.1-P1-15+squeeze6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Base support for javascript library packages</COMMENTS>
      <FILESIZE>76</FILESIZE>
      <FROM>deb</FROM>
      <NAME>javascript-common</NAME>
      <VERSION>7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Linux console font and keytable utilities</COMMENTS>
      <FILESIZE>1230</FILESIZE>
      <FROM>deb</FROM>
      <NAME>kbd</NAME>
      <VERSION>1.15.2-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>system-wide keyboard preferences</COMMENTS>
      <FILESIZE>1708</FILESIZE>
      <FROM>deb</FROM>
      <NAME>keyboard-configuration</NAME>
      <VERSION>1.68+squeeze2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>small utilities built with klibc for early boot</COMMENTS>
      <FILESIZE>440</FILESIZE>
      <FROM>deb</FROM>
      <NAME>klibc-utils</NAME>
      <VERSION>1.5.20-1+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>attempt to detect a laptop</COMMENTS>
      <FILESIZE>20</FILESIZE>
      <FROM>deb</FROM>
      <NAME>laptop-detect</NAME>
      <VERSION>0.13.7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>OpenLDAP utilities</COMMENTS>
      <FILESIZE>656</FILESIZE>
      <FROM>deb</FROM>
      <NAME>ldap-utils</NAME>
      <VERSION>2.4.23-7.2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>pager program similar to more</COMMENTS>
      <FILESIZE>288</FILESIZE>
      <FROM>deb</FROM>
      <NAME>less</NAME>
      <VERSION>436-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Access control list shared library</COMMENTS>
      <FILESIZE>88</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libacl1</NAME>
      <VERSION>2.2.49-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>module to find differences between files</COMMENTS>
      <FILESIZE>164</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libalgorithm-diff-perl</NAME>
      <VERSION>1.19.02-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>module to find differences between files (XS accelerated)</COMMENTS>
      <FILESIZE>100</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libalgorithm-diff-xs-perl</NAME>
      <VERSION>0.04-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Perl module for three-way merge of textual data</COMMENTS>
      <FILESIZE>44</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libalgorithm-merge-perl</NAME>
      <VERSION>0.08-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>server-side, HTML-embedded scripting language (Apache 2 module)</COMMENTS>
      <FILESIZE>7596</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libapache2-mod-php5</NAME>
      <VERSION>5.3.3-7+squeeze13</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The Apache Portable Runtime Library</COMMENTS>
      <FILESIZE>276</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libapr1</NAME>
      <VERSION>1.4.2-6+squeeze4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The Apache Portable Runtime Utility Library</COMMENTS>
      <FILESIZE>236</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libaprutil1</NAME>
      <VERSION>1.3.9+dfsg-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The Apache Portable Runtime Utility Library - SQLite3 Driver</COMMENTS>
      <FILESIZE>84</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libaprutil1-dbd-sqlite3</NAME>
      <VERSION>1.3.9+dfsg-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The Apache Portable Runtime Utility Library - LDAP Driver</COMMENTS>
      <FILESIZE>80</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libaprutil1-ldap</NAME>
      <VERSION>1.3.9+dfsg-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Extended attribute shared library</COMMENTS>
      <FILESIZE>64</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libattr1</NAME>
      <VERSION>1:2.4.44-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>block device id library</COMMENTS>
      <FILESIZE>212</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libblkid1</NAME>
      <VERSION>2.17.2-9</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Boost.Iostreams Library</COMMENTS>
      <FILESIZE>192</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libboost-iostreams1.42.0</NAME>
      <VERSION>1.42.0-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>utility functions from BSD systems - shared library</COMMENTS>
      <FILESIZE>124</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libbsd0</NAME>
      <VERSION>0.2.0-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>high-quality block-sorting file compressor library - runtime</COMMENTS>
      <FILESIZE>128</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libbz2-1.0</NAME>
      <VERSION>1.0.5-6+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Embedded GNU C Library: Binaries</COMMENTS>
      <FILESIZE>1520</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libc-bin</NAME>
      <VERSION>2.11.3-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Embedded GNU C Library: Development binaries</COMMENTS>
      <FILESIZE>348</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libc-dev-bin</NAME>
      <VERSION>2.11.3-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Embedded GNU C Library: Shared libraries</COMMENTS>
      <FILESIZE>9360</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libc6</NAME>
      <VERSION>2.11.3-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Embedded GNU C Library: Development Libraries and Header Files</COMMENTS>
      <FILESIZE>18544</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libc6-dev</NAME>
      <VERSION>2.11.3-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Embedded GNU C Library: Shared libraries [i686 optimized]</COMMENTS>
      <FILESIZE>2648</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libc6-i686</NAME>
      <VERSION>2.11.3-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>support for getting/setting POSIX.1e capabilities</COMMENTS>
      <FILESIZE>68</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libcap2</NAME>
      <VERSION>1:2.19-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>common error description library</COMMENTS>
      <FILESIZE>104</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libcomerr2</NAME>
      <VERSION>1.41.12-4stable1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>module that implements some sane defaults for Perl programs</COMMENTS>
      <FILESIZE>84</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libcommon-sense-perl</NAME>
      <VERSION>3.3-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>a generic Cascading Style Sheet (CSS) parsing and manipulation toolkit</COMMENTS>
      <FILESIZE>320</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libcroco3</NAME>
      <VERSION>0.6.2-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Multi-protocol file transfer library (GnuTLS)</COMMENTS>
      <FILESIZE>496</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libcurl3-gnutls</NAME>
      <VERSION>7.21.0-2.1+squeeze2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>high-level terminal interface library for C++ (runtime files)</COMMENTS>
      <FILESIZE>808</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libcwidget3</NAME>
      <VERSION>0.5.16-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Berkeley v4.7 Database Libraries [runtime]</COMMENTS>
      <FILESIZE>1432</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libdb4.7</NAME>
      <VERSION>4.7.25-9</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Berkeley v4.8 Database Libraries [runtime]</COMMENTS>
      <FILESIZE>1488</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libdb4.8</NAME>
      <VERSION>4.8.30-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Perl5 database interface to the MySQL database</COMMENTS>
      <FILESIZE>424</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libdbd-mysql-perl</NAME>
      <VERSION>4.016-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Perl Database Interface (DBI)</COMMENTS>
      <FILESIZE>2384</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libdbi-perl</NAME>
      <VERSION>1.612-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The Linux Kernel Device Mapper userspace library</COMMENTS>
      <FILESIZE>216</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libdevmapper1.02.1</NAME>
      <VERSION>2:1.02.48-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>hardware identification library</COMMENTS>
      <FILESIZE>332</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libdiscover2</NAME>
      <VERSION>2.1.2-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Dpkg perl modules</COMMENTS>
      <FILESIZE>1764</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libdpkg-perl</NAME>
      <VERSION>1.15.8.12</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>BSD editline and history libraries</COMMENTS>
      <FILESIZE>168</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libedit2</NAME>
      <VERSION>2.11-20080614-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>High-level library for managing Debian package information</COMMENTS>
      <FILESIZE>392</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libept1</NAME>
      <VERSION>1.0.4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Perl module for error/exception handling in an OO-ish way</COMMENTS>
      <FILESIZE>96</FILESIZE>
      <FROM>deb</FROM>
      <NAME>liberror-perl</NAME>
      <VERSION>0.17-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>An asynchronous event notification library</COMMENTS>
      <FILESIZE>152</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libevent-1.4-2</NAME>
      <VERSION>1.4.13-stable-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>XML parsing C library - runtime library</COMMENTS>
      <FILESIZE>368</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libexpat1</NAME>
      <VERSION>2.0.1-7+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Perl extension for recursively copying files and directories</COMMENTS>
      <FILESIZE>88</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libfile-copy-recursive-perl</NAME>
      <VERSION>0.38-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Perl module for searching paths for executable programs</COMMENTS>
      <FILESIZE>72</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libfile-which-perl</NAME>
      <VERSION>1.08-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Font::AFM - Interface to Adobe Font Metrics files</COMMENTS>
      <FILESIZE>120</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libfont-afm-perl</NAME>
      <VERSION>1.20-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>generic font configuration library - runtime</COMMENTS>
      <FILESIZE>412</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libfontconfig1</NAME>
      <VERSION>2.8.0-2.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>FreeType 2 font engine, shared library files</COMMENTS>
      <FILESIZE>668</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libfreetype6</NAME>
      <VERSION>2.4.2-2.1+squeeze4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GCC support library</COMMENTS>
      <FILESIZE>152</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libgcc1</NAME>
      <VERSION>1:4.4.5-8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>LGPL Crypto library - runtime library</COMMENTS>
      <FILESIZE>556</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libgcrypt11</NAME>
      <VERSION>1.4.5-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GD Graphics Library version 2</COMMENTS>
      <FILESIZE>648</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libgd2-xpm</NAME>
      <VERSION>2.0.36~rc1~dfsg-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU dbm database routines (runtime version)</COMMENTS>
      <FILESIZE>120</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libgdbm3</NAME>
      <VERSION>1.8.3-9</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GLib library of C routines</COMMENTS>
      <FILESIZE>2216</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libglib2.0-0</NAME>
      <VERSION>2.24.2-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Common files for GLib library</COMMENTS>
      <FILESIZE>4308</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libglib2.0-data</NAME>
      <VERSION>2.24.2-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Multiprecision arithmetic library</COMMENTS>
      <FILESIZE>680</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libgmp3c2</NAME>
      <VERSION>2:4.3.2+dfsg-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>the GNU TLS library - runtime library</COMMENTS>
      <FILESIZE>1264</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libgnutls26</NAME>
      <VERSION>2.8.6-1+squeeze2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GCC OpenMP (GOMP) support library</COMMENTS>
      <FILESIZE>84</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libgomp1</NAME>
      <VERSION>4.4.5-8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>library for common error values and messages in GnuPG components</COMMENTS>
      <FILESIZE>228</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libgpg-error0</NAME>
      <VERSION>1.6-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>MIT Kerberos runtime libraries - krb5 GSS-API Mechanism</COMMENTS>
      <FILESIZE>288</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libgssapi-krb5-2</NAME>
      <VERSION>1.8.3+dfsg-4squeeze6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>mechanism-switch gssapi library</COMMENTS>
      <FILESIZE>100</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libgssglue1</NAME>
      <VERSION>0.1-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>format HTML syntax trees into text, PostScript or RTF</COMMENTS>
      <FILESIZE>152</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libhtml-format-perl</NAME>
      <VERSION>2.04-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>collection of modules that parse HTML text documents</COMMENTS>
      <FILESIZE>320</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libhtml-parser-perl</NAME>
      <VERSION>3.66-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Data tables pertaining to HTML</COMMENTS>
      <FILESIZE>76</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libhtml-tagset-perl</NAME>
      <VERSION>3.20-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>module for using HTML Templates with Perl</COMMENTS>
      <FILESIZE>204</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libhtml-template-perl</NAME>
      <VERSION>2.9-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Perl module to represent and create HTML syntax trees</COMMENTS>
      <FILESIZE>520</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libhtml-tree-perl</NAME>
      <VERSION>3.23-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU Libidn library, implementation of IETF IDN specifications</COMMENTS>
      <FILESIZE>356</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libidn11</NAME>
      <VERSION>1.15-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The Independent JPEG Group&apos;s JPEG runtime library (version 6.2)</COMMENTS>
      <FILESIZE>204</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libjpeg62</NAME>
      <VERSION>6b1-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>JavaScript library for dynamic web applications</COMMENTS>
      <FILESIZE>296</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libjs-jquery</NAME>
      <VERSION>1.4.2-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Perl module to parse and convert to JSON</COMMENTS>
      <FILESIZE>264</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libjson-perl</NAME>
      <VERSION>2.21-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>module for serializing/deserializing JSON</COMMENTS>
      <FILESIZE>268</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libjson-xs-perl</NAME>
      <VERSION>2.290-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>MIT Kerberos runtime libraries - Crypto Library</COMMENTS>
      <FILESIZE>240</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libk5crypto3</NAME>
      <VERSION>1.8.3+dfsg-4squeeze6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Linux Key Management Utilities (library)</COMMENTS>
      <FILESIZE>56</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libkeyutils1</NAME>
      <VERSION>1.4-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>minimal libc subset for use with initramfs</COMMENTS>
      <FILESIZE>140</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libklibc</NAME>
      <VERSION>1.5.20-1+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>MIT Kerberos runtime libraries</COMMENTS>
      <FILESIZE>888</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libkrb5-3</NAME>
      <VERSION>1.8.3+dfsg-4squeeze6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>MIT Kerberos runtime libraries - Support library</COMMENTS>
      <FILESIZE>120</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libkrb5support0</NAME>
      <VERSION>1.8.3+dfsg-4squeeze6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>OpenLDAP libraries</COMMENTS>
      <FILESIZE>464</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libldap-2.4-2</NAME>
      <VERSION>2.4.23-7.2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Using libc functions for internationalization in Perl</COMMENTS>
      <FILESIZE>104</FILESIZE>
      <FROM>deb</FROM>
      <NAME>liblocale-gettext-perl</NAME>
      <VERSION>1.05-6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>A system independent dlopen wrapper for GNU libtool</COMMENTS>
      <FILESIZE>940</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libltdl-dev</NAME>
      <VERSION>2.2.6b-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>A system independent dlopen wrapper for GNU libtool</COMMENTS>
      <FILESIZE>376</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libltdl7</NAME>
      <VERSION>2.2.6b-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>XZ-format compression library</COMMENTS>
      <FILESIZE>320</FILESIZE>
      <FROM>deb</FROM>
      <NAME>liblzma2</NAME>
      <VERSION>5.0.0-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>File type determination library using &quot;magic&quot; numbers</COMMENTS>
      <FILESIZE>2044</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libmagic1</NAME>
      <VERSION>5.04-5+squeeze2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Manipulate email in perl programs</COMMENTS>
      <FILESIZE>276</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libmailtools-perl</NAME>
      <VERSION>2.06-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>multiple precision floating-point computation</COMMENTS>
      <FILESIZE>692</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libmpfr4</NAME>
      <VERSION>3.0.0-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>MySQL database client library</COMMENTS>
      <FILESIZE>4152</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libmysqlclient16</NAME>
      <VERSION>5.1.63-0+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>shared libraries for terminal handling</COMMENTS>
      <FILESIZE>592</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libncurses5</NAME>
      <VERSION>5.7+20100313-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>shared libraries for terminal handling (wide character support)</COMMENTS>
      <FILESIZE>640</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libncursesw5</NAME>
      <VERSION>5.7+20100313-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Perl module for building portable Perl daemons easily</COMMENTS>
      <FILESIZE>104</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libnet-daemon-perl</NAME>
      <VERSION>0.43-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Perl extension for manipulating IPv4/IPv6 addresses</COMMENTS>
      <FILESIZE>164</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libnet-ip-perl</NAME>
      <VERSION>1.25-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Perl module for Secure Sockets Layer (SSL)</COMMENTS>
      <FILESIZE>992</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libnet-ssleay-perl</NAME>
      <VERSION>1.36-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Not Erik&apos;s Windowing Toolkit - text mode windowing with slang</COMMENTS>
      <FILESIZE>960</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libnewt0.52</NAME>
      <VERSION>0.52.11-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Netfilter netlink library</COMMENTS>
      <FILESIZE>72</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libnfnetlink0</NAME>
      <VERSION>1.0.0-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>An nfs idmapping library</COMMENTS>
      <FILESIZE>120</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libnfsidmap2</NAME>
      <VERSION>0.23-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Oniguruma regular expressions library</COMMENTS>
      <FILESIZE>372</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libonig2</NAME>
      <VERSION>5.9.1-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Pluggable Authentication Modules for PAM</COMMENTS>
      <FILESIZE>992</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libpam-modules</NAME>
      <VERSION>1.1.1-6.1+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Runtime support for the PAM library</COMMENTS>
      <FILESIZE>1248</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libpam-runtime</NAME>
      <VERSION>1.1.1-6.1+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Pluggable Authentication Modules library</COMMENTS>
      <FILESIZE>244</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libpam0g</NAME>
      <VERSION>1.1.1-6.1+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Linux PCI Utilities (shared library)</COMMENTS>
      <FILESIZE>116</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libpci3</NAME>
      <VERSION>1:3.1.7-6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Perl 5 Compatible Regular Expression Library - runtime files</COMMENTS>
      <FILESIZE>480</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libpcre3</NAME>
      <VERSION>8.02-1.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>shared Perl library</COMMENTS>
      <FILESIZE>1392</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libperl5.10</NAME>
      <VERSION>5.10.1-17squeeze3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Perl extensions for writing PlRPC servers and clients</COMMENTS>
      <FILESIZE>100</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libplrpc-perl</NAME>
      <VERSION>0.2020-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>PNG library - runtime</COMMENTS>
      <FILESIZE>320</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libpng12-0</NAME>
      <VERSION>1.2.44-1+squeeze4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>lib for parsing cmdline parameters</COMMENTS>
      <FILESIZE>208</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libpopt0</NAME>
      <VERSION>1.16-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Run Perl program as a daemon process</COMMENTS>
      <FILESIZE>76</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libproc-daemon-perl</NAME>
      <VERSION>0.03-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Perl module for managing process id files</COMMENTS>
      <FILESIZE>80</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libproc-pid-file-perl</NAME>
      <VERSION>1.27-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>QDBM Database Libraries [runtime]</COMMENTS>
      <FILESIZE>368</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libqdbm14</NAME>
      <VERSION>1.8.77-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU readline and history libraries, run-time libraries</COMMENTS>
      <FILESIZE>356</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libreadline6</NAME>
      <VERSION>6.1-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>allows secure rpc communication using the rpcsec_gss protocol</COMMENTS>
      <FILESIZE>108</FILESIZE>
      <FROM>deb</FROM>
      <NAME>librpcsecgss3</NAME>
      <VERSION>0.19-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Cyrus SASL - authentication abstraction library</COMMENTS>
      <FILESIZE>248</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libsasl2-2</NAME>
      <VERSION>2.1.23.dfsg1-7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Cyrus SASL - pluggable authentication modules</COMMENTS>
      <FILESIZE>400</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libsasl2-modules</NAME>
      <VERSION>2.1.23.dfsg1-7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>SELinux runtime shared libraries</COMMENTS>
      <FILESIZE>216</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libselinux1</NAME>
      <VERSION>2.0.96-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>SELinux library for manipulating binary security policies</COMMENTS>
      <FILESIZE>300</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libsepol1</NAME>
      <VERSION>2.0.41-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>type-safe Signal Framework for C++ - runtime</COMMENTS>
      <FILESIZE>96</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libsigc++-2.0-0c2a</NAME>
      <VERSION>2.2.4.2-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The S-Lang programming library - runtime version</COMMENTS>
      <FILESIZE>1264</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libslang2</NAME>
      <VERSION>2.2.2-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>OpenSLP libraries</COMMENTS>
      <FILESIZE>160</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libslp1</NAME>
      <VERSION>1.2.1-7.8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>SQLite 3 shared library</COMMENTS>
      <FILESIZE>696</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libsqlite3-0</NAME>
      <VERSION>3.7.3-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>command-line interface parsing library</COMMENTS>
      <FILESIZE>112</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libss2</NAME>
      <VERSION>1.41.12-4stable1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>SSL shared libraries</COMMENTS>
      <FILESIZE>6956</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libssl0.9.8</NAME>
      <VERSION>0.9.8o-4squeeze13</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU Standard C++ Library v3</COMMENTS>
      <FILESIZE>1196</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libstdc++6</NAME>
      <VERSION>4.4.5-8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU Standard C++ Library v3 (development files)</COMMENTS>
      <FILESIZE>10160</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libstdc++6-4.4-dev</NAME>
      <VERSION>4.4.5-8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Type 1 font rasterizer library - runtime</COMMENTS>
      <FILESIZE>368</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libt1-5</NAME>
      <VERSION>5.1.2-3+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Manage ASN.1 structures (runtime)</COMMENTS>
      <FILESIZE>152</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libtasn1-3</NAME>
      <VERSION>2.7-1+squeeze+1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>get display widths of characters on the terminal</COMMENTS>
      <FILESIZE>92</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libtext-charwidth-perl</NAME>
      <VERSION>0.04-6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>converts between character sets in Perl</COMMENTS>
      <FILESIZE>104</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libtext-iconv-perl</NAME>
      <VERSION>1.7-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Text::Template perl module</COMMENTS>
      <FILESIZE>156</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libtext-template-perl</NAME>
      <VERSION>1.45-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>internationalized substitute of Text::Wrap</COMMENTS>
      <FILESIZE>28</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libtext-wrapi18n-perl</NAME>
      <VERSION>0.06-7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>collection of modules to manipulate date/time information</COMMENTS>
      <FILESIZE>248</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libtimedate-perl</NAME>
      <VERSION>1.2000-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Generic library support script</COMMENTS>
      <FILESIZE>1332</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libtool</NAME>
      <VERSION>2.2.6b-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>libudev shared library</COMMENTS>
      <FILESIZE>192</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libudev0</NAME>
      <VERSION>164-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Unicode string library for C</COMMENTS>
      <FILESIZE>1156</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libunistring0</NAME>
      <VERSION>0.9.3-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Load modules from a variable</COMMENTS>
      <FILESIZE>64</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libuniversal-require-perl</NAME>
      <VERSION>0.13-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>module to manipulate and access URI strings</COMMENTS>
      <FILESIZE>396</FILESIZE>
      <FROM>deb</FROM>
      <NAME>liburi-perl</NAME>
      <VERSION>1.60-1~bpo60+1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>userspace USB programming library</COMMENTS>
      <FILESIZE>96</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libusb-0.1-4</NAME>
      <VERSION>2:0.1.12-16</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Perl extension for using UUID interfaces as defined in e2fsprogs</COMMENTS>
      <FILESIZE>80</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libuuid-perl</NAME>
      <VERSION>0.02-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Universally Unique ID library</COMMENTS>
      <FILESIZE>116</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libuuid1</NAME>
      <VERSION>2.17.2-9</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Wietse Venema&apos;s TCP wrappers library</COMMENTS>
      <FILESIZE>120</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libwrap0</NAME>
      <VERSION>7.6.q-19</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Perl HTTP/WWW client/server library</COMMENTS>
      <FILESIZE>1076</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libwww-perl</NAME>
      <VERSION>5.836-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>X11 client-side library</COMMENTS>
      <FILESIZE>1356</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libx11-6</NAME>
      <VERSION>2:1.3.3-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>X11 client-side library</COMMENTS>
      <FILESIZE>2044</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libx11-data</NAME>
      <VERSION>2:1.3.3-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Search engine library</COMMENTS>
      <FILESIZE>4216</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libxapian22</NAME>
      <VERSION>1.2.3-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>X11 authorisation library</COMMENTS>
      <FILESIZE>64</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libxau6</NAME>
      <VERSION>1:1.0.6-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>X C Binding</COMMENTS>
      <FILESIZE>164</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libxcb1</NAME>
      <VERSION>1.6-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>X11 Display Manager Control Protocol library</COMMENTS>
      <FILESIZE>76</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libxdmcp6</NAME>
      <VERSION>1:1.0.3-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>X11 miscellaneous extension library</COMMENTS>
      <FILESIZE>132</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libxext6</NAME>
      <VERSION>2:1.1.2-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>XML::TreePP -- Pure Perl implementation for parsing/writing XML files</COMMENTS>
      <FILESIZE>104</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libxml-treepp-perl</NAME>
      <VERSION>0.39-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNOME XML library</COMMENTS>
      <FILESIZE>1588</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libxml2</NAME>
      <VERSION>2.7.8.dfsg-2+squeeze5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>X11 miscellaneous micro-utility library</COMMENTS>
      <FILESIZE>68</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libxmuu1</NAME>
      <VERSION>2:1.0.5-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>X11 pixmap library</COMMENTS>
      <FILESIZE>180</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libxpm4</NAME>
      <VERSION>1:3.5.8-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>XSLT 1.0 processing library - runtime library</COMMENTS>
      <FILESIZE>480</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libxslt1.1</NAME>
      <VERSION>1.1.26-6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>YAML Ain&apos;t Markup Language</COMMENTS>
      <FILESIZE>260</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libyaml-perl</NAME>
      <VERSION>0.71-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Perl module providing a fast, lightweight YAML loader and dumper</COMMENTS>
      <FILESIZE>260</FILESIZE>
      <FROM>deb</FROM>
      <NAME>libyaml-syck-perl</NAME>
      <VERSION>1.12-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Linux image base package</COMMENTS>
      <FILESIZE>292</FILESIZE>
      <FROM>deb</FROM>
      <NAME>linux-base</NAME>
      <VERSION>2.6.32-45</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Linux 2.6 for modern PCs (meta-package)</COMMENTS>
      <FILESIZE>48</FILESIZE>
      <FROM>deb</FROM>
      <NAME>linux-image-2.6-686</NAME>
      <VERSION>2.6.32+29</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Linux 2.6.32 for modern PCs</COMMENTS>
      <FILESIZE>77900</FILESIZE>
      <FROM>deb</FROM>
      <NAME>linux-image-2.6.32-5-686</NAME>
      <VERSION>2.6.32-45</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Linux support headers for userspace development</COMMENTS>
      <FILESIZE>4084</FILESIZE>
      <FROM>deb</FROM>
      <NAME>linux-libc-dev</NAME>
      <VERSION>2.6.32-45</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Embedded GNU C Library: National Language (locale) data [support]</COMMENTS>
      <FILESIZE>12536</FILESIZE>
      <FROM>deb</FROM>
      <NAME>locales</NAME>
      <VERSION>2.11.3-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>system login tools</COMMENTS>
      <FILESIZE>2528</FILESIZE>
      <FROM>deb</FROM>
      <NAME>login</NAME>
      <VERSION>1:4.1.4.2+svn3283-2+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Log rotation utility</COMMENTS>
      <FILESIZE>100</FILESIZE>
      <FROM>deb</FROM>
      <NAME>logrotate</NAME>
      <VERSION>3.7.8-6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Linux Standard Base 3.2 init script functionality</COMMENTS>
      <FILESIZE>32</FILESIZE>
      <FROM>deb</FROM>
      <NAME>lsb-base</NAME>
      <VERSION>3.2-23.2squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Text-mode WWW Browser (transitional package)</COMMENTS>
      <FILESIZE>252</FILESIZE>
      <FROM>deb</FROM>
      <NAME>lynx</NAME>
      <VERSION>2.8.8dev.5-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Text-mode WWW Browser with NLS support (development version)</COMMENTS>
      <FILESIZE>4932</FILESIZE>
      <FROM>deb</FROM>
      <NAME>lynx-cur</NAME>
      <VERSION>2.8.8dev.5-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>a macro processing language</COMMENTS>
      <FILESIZE>636</FILESIZE>
      <FROM>deb</FROM>
      <NAME>m4</NAME>
      <VERSION>1.4.14-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>An utility for Directing compilation.</COMMENTS>
      <FILESIZE>1204</FILESIZE>
      <FROM>deb</FROM>
      <NAME>make</NAME>
      <VERSION>3.81-8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>on-line manual pager</COMMENTS>
      <FILESIZE>3000</FILESIZE>
      <FROM>deb</FROM>
      <NAME>man-db</NAME>
      <VERSION>2.5.7-8</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Manual pages about using a GNU/Linux system</COMMENTS>
      <FILESIZE>1128</FILESIZE>
      <FROM>deb</FROM>
      <NAME>manpages</NAME>
      <VERSION>3.27-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Manual pages about using GNU/Linux for development</COMMENTS>
      <FILESIZE>3344</FILESIZE>
      <FROM>deb</FROM>
      <NAME>manpages-dev</NAME>
      <VERSION>3.27-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>a pattern scanning and text processing language</COMMENTS>
      <FILESIZE>228</FILESIZE>
      <FROM>deb</FROM>
      <NAME>mawk</NAME>
      <VERSION>1.3.3-15</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>MIME files &apos;mime.types&apos; &amp; &apos;mailcap&apos;, and support programs</COMMENTS>
      <FILESIZE>188</FILESIZE>
      <FROM>deb</FROM>
      <NAME>mime-support</NAME>
      <VERSION>3.48-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>tools for managing Linux kernel modules</COMMENTS>
      <FILESIZE>332</FILESIZE>
      <FROM>deb</FROM>
      <NAME>module-init-tools</NAME>
      <VERSION>3.12-2+b1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Tools for mounting and manipulating filesystems</COMMENTS>
      <FILESIZE>356</FILESIZE>
      <FROM>deb</FROM>
      <NAME>mount</NAME>
      <VERSION>2.17.2-9</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>MySQL database client binaries</COMMENTS>
      <FILESIZE>22340</FILESIZE>
      <FROM>deb</FROM>
      <NAME>mysql-client-5.1</NAME>
      <VERSION>5.1.63-0+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>MySQL database common files, e.g. /etc/mysql/my.cnf</COMMENTS>
      <FILESIZE>156</FILESIZE>
      <FROM>deb</FROM>
      <NAME>mysql-common</NAME>
      <VERSION>5.1.63-0+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>MySQL database server (metapackage depending on the latest version)</COMMENTS>
      <FILESIZE>96</FILESIZE>
      <FROM>deb</FROM>
      <NAME>mysql-server</NAME>
      <VERSION>5.1.63-0+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>MySQL database server binaries and system database setup</COMMENTS>
      <FILESIZE>14008</FILESIZE>
      <FROM>deb</FROM>
      <NAME>mysql-server-5.1</NAME>
      <VERSION>5.1.63-0+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>MySQL database server binaries</COMMENTS>
      <FILESIZE>9688</FILESIZE>
      <FROM>deb</FROM>
      <NAME>mysql-server-core-5.1</NAME>
      <VERSION>5.1.63-0+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>small, friendly text editor inspired by Pico</COMMENTS>
      <FILESIZE>1752</FILESIZE>
      <FROM>deb</FROM>
      <NAME>nano</NAME>
      <VERSION>2.2.4-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>basic terminal type definitions</COMMENTS>
      <FILESIZE>452</FILESIZE>
      <FROM>deb</FROM>
      <NAME>ncurses-base</NAME>
      <VERSION>5.7+20100313-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>terminal-related programs and man pages</COMMENTS>
      <FILESIZE>500</FILESIZE>
      <FROM>deb</FROM>
      <NAME>ncurses-bin</NAME>
      <VERSION>5.7+20100313-5</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The NET-3 networking toolkit</COMMENTS>
      <FILESIZE>948</FILESIZE>
      <FROM>deb</FROM>
      <NAME>net-tools</NAME>
      <VERSION>1.60-23</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Basic TCP/IP networking system</COMMENTS>
      <FILESIZE>96</FILESIZE>
      <FROM>deb</FROM>
      <NAME>netbase</NAME>
      <VERSION>4.45</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>TCP/IP swiss army knife</COMMENTS>
      <FILESIZE>192</FILESIZE>
      <FROM>deb</FROM>
      <NAME>netcat-traditional</NAME>
      <VERSION>1.10-38</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>NFS support files common to client and server</COMMENTS>
      <FILESIZE>604</FILESIZE>
      <FROM>deb</FROM>
      <NAME>nfs-common</NAME>
      <VERSION>1:1.2.2-4squeeze2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>support for NFS kernel server</COMMENTS>
      <FILESIZE>384</FILESIZE>
      <FROM>deb</FROM>
      <NAME>nfs-kernel-server</NAME>
      <VERSION>1:1.2.2-4squeeze2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Nullsoft Scriptable Install System (modified for Debian)</COMMENTS>
      <FILESIZE>5788</FILESIZE>
      <FROM>deb</FROM>
      <NAME>nsis</NAME>
      <VERSION>2.46-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Helper program for accessing odbc ini files</COMMENTS>
      <FILESIZE>104</FILESIZE>
      <FROM>deb</FROM>
      <NAME>odbcinst</NAME>
      <VERSION>2.2.14p2-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Support library for accessing odbc ini files</COMMENTS>
      <FILESIZE>240</FILESIZE>
      <FROM>deb</FROM>
      <NAME>odbcinst1debian2</NAME>
      <VERSION>2.2.14p2-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The OpenBSD Internet Superserver</COMMENTS>
      <FILESIZE>136</FILESIZE>
      <FROM>deb</FROM>
      <NAME>openbsd-inetd</NAME>
      <VERSION>0.20080125-6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>list of default blacklisted OpenSSH RSA and DSA keys</COMMENTS>
      <FILESIZE>4092</FILESIZE>
      <FROM>deb</FROM>
      <NAME>openssh-blacklist</NAME>
      <VERSION>0.4.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>list of non-default blacklisted OpenSSH RSA and DSA keys</COMMENTS>
      <FILESIZE>4100</FILESIZE>
      <FROM>deb</FROM>
      <NAME>openssh-blacklist-extra</NAME>
      <VERSION>0.4.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>secure shell (SSH) client, for secure access to remote machines</COMMENTS>
      <FILESIZE>2092</FILESIZE>
      <FROM>deb</FROM>
      <NAME>openssh-client</NAME>
      <VERSION>1:5.5p1-6+squeeze2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>secure shell (SSH) server, for secure access from remote machines</COMMENTS>
      <FILESIZE>768</FILESIZE>
      <FROM>deb</FROM>
      <NAME>openssh-server</NAME>
      <VERSION>1:5.5p1-6+squeeze2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Secure Socket Layer (SSL) binary and related cryptographic tools</COMMENTS>
      <FILESIZE>2376</FILESIZE>
      <FROM>deb</FROM>
      <NAME>openssl</NAME>
      <VERSION>0.9.8o-4squeeze13</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>utility to detect other OSes on a set of drives</COMMENTS>
      <FILESIZE>184</FILESIZE>
      <FROM>deb</FROM>
      <NAME>os-prober</NAME>
      <VERSION>1.42</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>7z and 7za file archivers with high compression ratio</COMMENTS>
      <FILESIZE>3267</FILESIZE>
      <FROM>deb</FROM>
      <NAME>p7zip-full</NAME>
      <VERSION>9.04~dfsg.1-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>change and administer password and group data</COMMENTS>
      <FILESIZE>2572</FILESIZE>
      <FROM>deb</FROM>
      <NAME>passwd</NAME>
      <VERSION>1:4.1.4.2+svn3283-2+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Apply a diff file to an original</COMMENTS>
      <FILESIZE>244</FILESIZE>
      <FROM>deb</FROM>
      <NAME>patch</NAME>
      <VERSION>2.6-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Linux PCI Utilities</COMMENTS>
      <FILESIZE>896</FILESIZE>
      <FROM>deb</FROM>
      <NAME>pciutils</NAME>
      <VERSION>1:3.1.7-6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Larry Wall&apos;s Practical Extraction and Report Language</COMMENTS>
      <FILESIZE>13172</FILESIZE>
      <FROM>deb</FROM>
      <NAME>perl</NAME>
      <VERSION>5.10.1-17squeeze3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>minimal Perl system</COMMENTS>
      <FILESIZE>4492</FILESIZE>
      <FROM>deb</FROM>
      <NAME>perl-base</NAME>
      <VERSION>5.10.1-17squeeze3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Core Perl modules</COMMENTS>
      <FILESIZE>15856</FILESIZE>
      <FROM>deb</FROM>
      <NAME>perl-modules</NAME>
      <VERSION>5.10.1-17squeeze3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>command-line interpreter for the php5 scripting language</COMMENTS>
      <FILESIZE>7380</FILESIZE>
      <FROM>deb</FROM>
      <NAME>php5-cli</NAME>
      <VERSION>5.3.3-7+squeeze13</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Common files for packages built from the php5 source</COMMENTS>
      <FILESIZE>896</FILESIZE>
      <FROM>deb</FROM>
      <NAME>php5-common</NAME>
      <VERSION>5.3.3-7+squeeze13</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GD module for php5</COMMENTS>
      <FILESIZE>152</FILESIZE>
      <FROM>deb</FROM>
      <NAME>php5-gd</NAME>
      <VERSION>5.3.3-7+squeeze13</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>advanced protection module for php5</COMMENTS>
      <FILESIZE>236</FILESIZE>
      <FROM>deb</FROM>
      <NAME>php5-suhosin</NAME>
      <VERSION>0.9.32.1-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>XML-RPC module for php5</COMMENTS>
      <FILESIZE>128</FILESIZE>
      <FROM>deb</FROM>
      <NAME>php5-xmlrpc</NAME>
      <VERSION>5.3.3-7+squeeze13</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>RPC port mapper</COMMENTS>
      <FILESIZE>160</FILESIZE>
      <FROM>deb</FROM>
      <NAME>portmap</NAME>
      <VERSION>6.0.0-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>/proc file system utilities</COMMENTS>
      <FILESIZE>680</FILESIZE>
      <FROM>deb</FROM>
      <NAME>procps</NAME>
      <VERSION>1:3.2.8-9squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>utilities that use the proc file system</COMMENTS>
      <FILESIZE>668</FILESIZE>
      <FROM>deb</FROM>
      <NAME>psmisc</NAME>
      <VERSION>22.11-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>interactive high-level object-oriented language (default version)</COMMENTS>
      <FILESIZE>736</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python</NAME>
      <VERSION>2.6.6-3+squeeze7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>register and build utility for Python packages</COMMENTS>
      <FILESIZE>332</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-central</NAME>
      <VERSION>0.6.16+nmu1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>simple but powerful config file reader and writer for Python</COMMENTS>
      <FILESIZE>1656</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-configobj</NAME>
      <VERSION>4.7.2+ds-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>cryptographic algorithms and protocols for Python</COMMENTS>
      <FILESIZE>4356</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-crypto</NAME>
      <VERSION>2.1.0-2+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>LDAP interface module for Python</COMMENTS>
      <FILESIZE>400</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-ldap</NAME>
      <VERSION>2.3.11-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>minimal subset of the Python language (default version)</COMMENTS>
      <FILESIZE>184</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-minimal</NAME>
      <VERSION>2.6.6-3+squeeze7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>process-based &quot;threading&quot; interface</COMMENTS>
      <FILESIZE>1048</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-multiprocessing</NAME>
      <VERSION>2.6.2.1-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>A Python interface to MySQL</COMMENTS>
      <FILESIZE>328</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-mysqldb</NAME>
      <VERSION>1.2.2-10+b1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Python wrapper around the OpenSSL library</COMMENTS>
      <FILESIZE>472</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-openssl</NAME>
      <VERSION>0.10-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>A Python interface to the PAM library</COMMENTS>
      <FILESIZE>120</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-pam</NAME>
      <VERSION>0.4.2-12.2+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Package Discovery and Resource Access using pkg_resources</COMMENTS>
      <FILESIZE>204</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-pkg-resources</NAME>
      <VERSION>0.6.14-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>ASN.1 library for Python</COMMENTS>
      <FILESIZE>292</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-pyasn1</NAME>
      <VERSION>0.0.11a-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>pyserial - module encapsulating access for the serial port</COMMENTS>
      <FILESIZE>264</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-serial</NAME>
      <VERSION>2.3-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>SQL toolkit and Object Relational Mapper for Python</COMMENTS>
      <FILESIZE>3288</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-sqlalchemy</NAME>
      <VERSION>0.6.3-3+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>SQL toolkit and Object Relational Mapper for Python - C extension</COMMENTS>
      <FILESIZE>136</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-sqlalchemy-ext</NAME>
      <VERSION>0.6.3-3+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>automated rebuilding support for Python modules</COMMENTS>
      <FILESIZE>216</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-support</NAME>
      <VERSION>1.0.10</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Event-based framework for internet applications (transitional package)</COMMENTS>
      <FILESIZE>88</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-twisted</NAME>
      <VERSION>10.1.0-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Event-based framework for internet applications</COMMENTS>
      <FILESIZE>304</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-twisted-bin</NAME>
      <VERSION>10.1.0-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>The Twisted SSH Implementation</COMMENTS>
      <FILESIZE>2052</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-twisted-conch</NAME>
      <VERSION>1:10.1.0-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Event-based framework for internet applications</COMMENTS>
      <FILESIZE>8020</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-twisted-core</NAME>
      <VERSION>10.1.0-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Documentation generator with HTML and LaTeX support</COMMENTS>
      <FILESIZE>864</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-twisted-lore</NAME>
      <VERSION>10.1.0-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>An SMTP, IMAP and POP protocol implementation</COMMENTS>
      <FILESIZE>1232</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-twisted-mail</NAME>
      <VERSION>10.1.0-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>A DNS protocol implementation with client and server</COMMENTS>
      <FILESIZE>576</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-twisted-names</NAME>
      <VERSION>10.1.0-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>An NNTP protocol implementation with client and server</COMMENTS>
      <FILESIZE>264</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-twisted-news</NAME>
      <VERSION>10.1.0-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Process management, including an inetd server</COMMENTS>
      <FILESIZE>292</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-twisted-runner</NAME>
      <VERSION>10.1.0-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>An HTTP protocol implementation together with clients and servers</COMMENTS>
      <FILESIZE>2032</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-twisted-web</NAME>
      <VERSION>10.1.0-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Chat and Instant Messaging</COMMENTS>
      <FILESIZE>1804</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-twisted-words</NAME>
      <VERSION>10.1.0-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Interfaces for Python</COMMENTS>
      <FILESIZE>756</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python-zope.interface</NAME>
      <VERSION>3.5.3-1+b1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>An interactive high-level object-oriented language (version 2.5)</COMMENTS>
      <FILESIZE>10196</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python2.5</NAME>
      <VERSION>2.5.5-11</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>A minimal subset of the Python language (version 2.5)</COMMENTS>
      <FILESIZE>4368</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python2.5-minimal</NAME>
      <VERSION>2.5.5-11</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>An interactive high-level object-oriented language (version 2.6)</COMMENTS>
      <FILESIZE>8976</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python2.6</NAME>
      <VERSION>2.6.6-8+b1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>A minimal subset of the Python language (version 2.6)</COMMENTS>
      <FILESIZE>4904</FILESIZE>
      <FROM>deb</FROM>
      <NAME>python2.6-minimal</NAME>
      <VERSION>2.6.6-8+b1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>GNU readline and history libraries, common files</COMMENTS>
      <FILESIZE>92</FILESIZE>
      <FROM>deb</FROM>
      <NAME>readline-common</NAME>
      <VERSION>6.1-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>fast remote file copy program (like rcp)</COMMENTS>
      <FILESIZE>676</FILESIZE>
      <FROM>deb</FROM>
      <NAME>rsync</NAME>
      <VERSION>3.0.7-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>enhanced multi-threaded syslogd</COMMENTS>
      <FILESIZE>732</FILESIZE>
      <FROM>deb</FROM>
      <NAME>rsyslog</NAME>
      <VERSION>4.6.4-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>The GNU sed stream editor</COMMENTS>
      <FILESIZE>956</FILESIZE>
      <FROM>deb</FROM>
      <NAME>sed</NAME>
      <VERSION>4.2.1-7</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Utilities for sensible alternative selection</COMMENTS>
      <FILESIZE>112</FILESIZE>
      <FROM>deb</FROM>
      <NAME>sensible-utils</NAME>
      <VERSION>0.0.4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>SGML infrastructure and SGML catalog file support</COMMENTS>
      <FILESIZE>148</FILESIZE>
      <FROM>deb</FROM>
      <NAME>sgml-base</NAME>
      <VERSION>1.26+nmu1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>common SGML and XML data</COMMENTS>
      <FILESIZE>1704</FILESIZE>
      <FROM>deb</FROM>
      <NAME>sgml-data</NAME>
      <VERSION>2.0.4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>FreeDesktop.org shared MIME database and spec</COMMENTS>
      <FILESIZE>3348</FILESIZE>
      <FROM>deb</FROM>
      <NAME>shared-mime-info</NAME>
      <VERSION>0.71-4</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>OpenLDAP server (slapd)</COMMENTS>
      <FILESIZE>3824</FILESIZE>
      <FROM>deb</FROM>
      <NAME>slapd</NAME>
      <VERSION>2.4.23-7.2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>simple debconf wrapper for OpenSSL</COMMENTS>
      <FILESIZE>112</FILESIZE>
      <FROM>deb</FROM>
      <NAME>ssl-cert</NAME>
      <VERSION>1.0.28</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>System-V-like runlevel change mechanism</COMMENTS>
      <FILESIZE>300</FILESIZE>
      <FROM>deb</FROM>
      <NAME>sysv-rc</NAME>
      <VERSION>2.88dsf-13.1+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>System-V-like init utilities</COMMENTS>
      <FILESIZE>248</FILESIZE>
      <FROM>deb</FROM>
      <NAME>sysvinit</NAME>
      <VERSION>2.88dsf-13.1+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>System-V-like utilities</COMMENTS>
      <FILESIZE>260</FILESIZE>
      <FROM>deb</FROM>
      <NAME>sysvinit-utils</NAME>
      <VERSION>2.88dsf-13.1+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>GNU version of the tar archiving utility</COMMENTS>
      <FILESIZE>2392</FILESIZE>
      <FROM>deb</FROM>
      <NAME>tar</NAME>
      <VERSION>1.23-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Tool for selecting tasks for installation on Debian systems</COMMENTS>
      <FILESIZE>904</FILESIZE>
      <FROM>deb</FROM>
      <NAME>tasksel</NAME>
      <VERSION>2.88</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Official tasks used for installation of Debian systems</COMMENTS>
      <FILESIZE>984</FILESIZE>
      <FROM>deb</FROM>
      <NAME>tasksel-data</NAME>
      <VERSION>2.88</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Wietse Venema&apos;s TCP wrapper utilities</COMMENTS>
      <FILESIZE>128</FILESIZE>
      <FROM>deb</FROM>
      <NAME>tcpd</NAME>
      <VERSION>7.6.q-19</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Trivial file transfer protocol server</COMMENTS>
      <FILESIZE>80</FILESIZE>
      <FROM>deb</FROM>
      <NAME>tftpd</NAME>
      <VERSION>0.17-18</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Traces the route taken by packets over an IPv4/IPv6 network</COMMENTS>
      <FILESIZE>176</FILESIZE>
      <FROM>deb</FROM>
      <NAME>traceroute</NAME>
      <VERSION>1:2.0.15-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Vera font family derivate with additional characters</COMMENTS>
      <FILESIZE>2592</FILESIZE>
      <FROM>deb</FROM>
      <NAME>ttf-dejavu-core</NAME>
      <VERSION>2.31-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>time zone and daylight-saving time data</COMMENTS>
      <FILESIZE>6268</FILESIZE>
      <FROM>deb</FROM>
      <NAME>tzdata</NAME>
      <VERSION>2012c-0squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Update Configuration File: preserve user changes to config files.</COMMENTS>
      <FILESIZE>268</FILESIZE>
      <FROM>deb</FROM>
      <NAME>ucf</NAME>
      <VERSION>3.0025+nmu1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>/dev/ and hotplug management daemon</COMMENTS>
      <FILESIZE>1644</FILESIZE>
      <FROM>deb</FROM>
      <NAME>udev</NAME>
      <VERSION>164-3</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>ODBC tools libraries</COMMENTS>
      <FILESIZE>696</FILESIZE>
      <FROM>deb</FROM>
      <NAME>unixodbc</NAME>
      <VERSION>2.2.14p2-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>inetd configuration file updater</COMMENTS>
      <FILESIZE>128</FILESIZE>
      <FROM>deb</FROM>
      <NAME>update-inetd</NAME>
      <VERSION>4.38+nmu1+squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Linux USB utilities</COMMENTS>
      <FILESIZE>640</FILESIZE>
      <FROM>deb</FROM>
      <NAME>usbutils</NAME>
      <VERSION>0.87-5squeeze1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Miscellaneous system utilities</COMMENTS>
      <FILESIZE>2112</FILESIZE>
      <FROM>deb</FROM>
      <NAME>util-linux</NAME>
      <VERSION>2.17.2-9</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Vi IMproved - Common files</COMMENTS>
      <FILESIZE>364</FILESIZE>
      <FROM>deb</FROM>
      <NAME>vim-common</NAME>
      <VERSION>2:7.2.445+hg~cb94c42c0e1a-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Vi IMproved - enhanced vi editor - compact version</COMMENTS>
      <FILESIZE>720</FILESIZE>
      <FROM>deb</FROM>
      <NAME>vim-tiny</NAME>
      <VERSION>2:7.2.445+hg~cb94c42c0e1a-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>retrieves files from the web</COMMENTS>
      <FILESIZE>2312</FILESIZE>
      <FROM>deb</FROM>
      <NAME>wget</NAME>
      <VERSION>1.12-2.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>Displays user-friendly dialog boxes from shell scripts</COMMENTS>
      <FILESIZE>100</FILESIZE>
      <FROM>deb</FROM>
      <NAME>whiptail</NAME>
      <VERSION>0.52.11-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>Debian web auto configuration</COMMENTS>
      <FILESIZE>192</FILESIZE>
      <FROM>deb</FROM>
      <NAME>wwwconfig-common</NAME>
      <VERSION>0.2.1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>X authentication utility</COMMENTS>
      <FILESIZE>96</FILESIZE>
      <FROM>deb</FROM>
      <NAME>xauth</NAME>
      <VERSION>1:1.0.4-1</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>X Keyboard Extension (XKB) configuration data</COMMENTS>
      <FILESIZE>4864</FILESIZE>
      <FROM>deb</FROM>
      <NAME>xkb-data</NAME>
      <VERSION>1.8-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>all</ARCH>
      <COMMENTS>XML infrastructure and XML catalog file support</COMMENTS>
      <FILESIZE>260</FILESIZE>
      <FROM>deb</FROM>
      <NAME>xml-core</NAME>
      <VERSION>0.13</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>XSLT 1.0 command line processor</COMMENTS>
      <FILESIZE>180</FILESIZE>
      <FROM>deb</FROM>
      <NAME>xsltproc</NAME>
      <VERSION>1.1.26-6</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>XZ-format compression utilities</COMMENTS>
      <FILESIZE>452</FILESIZE>
      <FROM>deb</FROM>
      <NAME>xz-utils</NAME>
      <VERSION>5.0.0-2</VERSION>
    </SOFTWARES>
    <SOFTWARES>
      <ARCH>i386</ARCH>
      <COMMENTS>compression library - runtime</COMMENTS>
      <FILESIZE>160</FILESIZE>
      <FROM>deb</FROM>
      <NAME>zlib1g</NAME>
      <VERSION>1:1.2.3.4.dfsg-3</VERSION>
    </SOFTWARES>
    <SOUNDS>
      <DESCRIPTION>rev 01</DESCRIPTION>
      <MANUFACTURER>Intel Corporation 82801FB/FBM/FR/FW/FRW (ICH6 Family) High Definition Audio Controller</MANUFACTURER>
      <NAME>Audio device</NAME>
    </SOUNDS>
    <STORAGES>
      <DESCRIPTION>Virtual</DESCRIPTION>
      <MANUFACTURER>6900</MANUFACTURER>
      <NAME>vda</NAME>
      <SERIALNUMBER />  <TYPE>disk</TYPE>
    </STORAGES>
    <USERS>
      <LOGIN>root</LOGIN>
    </USERS>
    <VERSIONCLIENT>FusionInventory-Agent_v2.2.3</VERSIONCLIENT>
  </CONTENT>
  <DEVICEID>debian6-2012-11-26-15-02-19</DEVICEID>
  <QUERY>INVENTORY</QUERY>
</REQUEST>
"""

if __name__ == "__main__" :
    unittest.main()


