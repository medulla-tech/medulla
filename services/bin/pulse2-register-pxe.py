#!/usr/bin/python
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
import xml.etree.ElementTree as ET  # form XML Building
from pulse2.package_server.config import P2PServerCP
from mmc.site import mmcconfdir
import sys
import ConfigParser
#from optparse import OptionParser
import logging
import getopt
conf ={}
logger = logging.getLogger('pulse2-register-pxe')
hdlr = logging.FileHandler('/var/log/mmc/pulse2-register-pxe.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)

def senddata(query,ip ="127.0.0.1", port =1001 ):
    adresse=(ip,port)
    monSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logger.debug("Send PXE xml for registration :%s"% query)
    monSocket.sendto("\xBB%s" % query, adresse)
    time.sleep(0.2)
    monSocket.sendto("\xBA%s" % query, adresse)
    time.sleep(0.2)
    monSocket.sendto("\xBA%s" % query, adresse)
    monSocket.close()

def mac_adressexml(file_content):
    root = ET.fromstring(file_content)
    for child in root:
        if child.tag == "CONTENT":
            for cc in child:
                if cc.tag == "NETWORKS":
                    for dd in cc:
                        if dd.tag == "MACADDR":
                            return dd.text
    return ""

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
        logger.debug("CREATE event:%s"% event.pathname)
        time.sleep(0.005)
        self.traitement(event.pathname)

    def process_IN_DELETE(self, event):
        print "DELETE event:", event.pathname

    def process_IN_MODIFY(self, event):
        logger.debug("MODIFY event: %s"% event.pathname)
        time.sleep(0.025)
        self.traitement(event.pathname)

    def process_IN_OPEN(self, event):
        print "OPEN event:"

    def traitement(self, name):
        if os.path.isfile(str(name)):
            file_content=""
            try:
                with gzip.open(str(name), 'rb') as f:
                    file_content = f.read()
                    f.close()
                m = re.search('<REQUEST>.*<\/REQUEST>', file_content)
                file_content = str(m.group(0))
                file_content=file_content.replace('\\n','')
                file_content=file_content.replace('\\t','')
                try:
                    mac = mac_adressexml(file_content)
                    try:
                        # add Mc:mac address end of datagram
                        header='<?xml version="1.0" encoding="utf-8"?>'
                        xmldata="%s%s\nMc:%s"%(header,file_content,mac)
                        logger.debug("XML recv from pxe client %s"% xmldata)
                        os.remove(name)
                        senddata(xmldata,'127.0.0.1',conf['port'])
                    except:
                        logger.error("UDP error sending to %s:%d"%('127.0.0.1',conf['port']))
                except:
                    logger.error("MAC address error")
            except:
                logger.error("Error extracting file %s"%str(name))

class watchInventory:
    def __init__(self):
        #threading.Thread.__init__(self)
        self.eh = MyEventHandler()
        logger.debug("install inotify")

    def run(self):
        self.wm = pyinotify.WatchManager()
        #self.mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE  # watched events
        self.notifier = pyinotify.ThreadedNotifier(self.wm, self.eh)
        self.notifier.start()
        mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY  # watched eventspyinotify.IN_DELETE |
        self.wm.add_watch( '/var/lib/pulse2/imaging/inventories',mask, rec=True)

    def stop(self):
        self.notifier.stop()

if __name__ == '__main__':
    inifile = mmcconfdir + "/pulse2/package-server/package-server.ini"
    pidfile="/var/run/pulse2-register-pxe.pid"
    cp = None
    mode = logging.WARNING
    try:
        opts, suivarg = getopt.getopt(sys.argv[1:], "f:dh")
    except getopt.GetoptError:
        sys.exit(2)
    daemonize = True
    for option, argument in opts:
        if option == "-f":
            inifile = argument
        elif option == "-d":
            daemonize = False
            mode = logging.DEBUG
            print "pid file: %d\n"%os.getpid()
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

    conf['ip']="127.0.0.1"
    if cp.has_option('imaging_api', 'pxe_port'):
        conf['port']=int(cp.get('imaging_api', 'pxe_port'))
    else:
        conf['port']=1001
    if cp.has_option('debug', 'mode'):
        mode=cp.get('network', 'port')
    if daemonize:
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            print >>sys.stderr, "Fork #1 failed: %d (%s)" % (e.errno, e.strerror)
            sys.exit(1)
        # decouple from parent environment
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
                os.seteuid(0)
                os.setegid(0)
                logger.debug("PID file" + str(pid) + " > " + pidfile)
                os.system("echo " + str(pid) + " > " + pidfile)
                sys.exit(0)
        except OSError, e:
            print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
            sys.exit(1)
    try:
        logger.setLevel(mode)
        logger.debug("Debug mode")
        a = watchInventory()
        a.run()
    except KeyboardInterrupt:
        a.stop()
        sys.exit(3)
