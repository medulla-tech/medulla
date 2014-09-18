# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import nmap
import sys
import os

from mmc.plugins.monitoring.config import MonitoringConfig
# Database
from pulse2.database.monitoring import MonitoringDatabase


def get_host_os(ip):
	try:
	    nm = nmap.PortScanner()         
	except nmap.PortScannerError:
    		print('Nmap not found', sys.exc_info()[0])
    		sys.exit(0)
	except:
    		print("Unexpected error:", sys.exc_info()[0])
    		sys.exit(0)
	if (os.getuid() != 0):
		return 0

	nm.scan(ip, arguments='-O')

        if nm[ip].has_key('osmatch'):
                for osmatch in nm[ip]['osmatch']:
                        print('OsMatch.name : {0}'.format(osmatch['name']))
                        print('OsMatch.accuracy : {0}'.format(osmatch['accuracy']))
                        print('OsMatch.line : {0}'.format(osmatch['line']))
                        print('')
                return nm[ip]['osmatch']

	if nm[ip].has_key('osclass'):
	        for osclass in nm[ip]['osclass']:
	            	print('OsClass.type : {0}'.format(osclass['type']))
        	    	print('OsClass.vendor : {0}'.format(osclass['vendor']))
			print('OsClass.osfamily : {0}'.format(osclass['osfamily']))
			print('OsClass.osgen : {0}'.format(osclass['osgen']))
            		print('OsClass.accuracy : {0}'.format(osclass['accuracy']))
           		print('')
		return nm[ip]['osclass']


	if nm[ip].has_key('fingerprint'):
        	print('Fingerprint : {0}'.format(nm[ip]['fingerprint']))
		return nm[ip]['fingerprint']

	return 0

def get_task_host_os():
        try:
            nm = nmap.PortScanner()
        except nmap.PortScannerError:
                print('Nmap not found', sys.exc_info()[0])
                sys.exit(0)
        except:
                print("Unexpected error:", sys.exc_info()[0])
                sys.exit(0)
        if (os.getuid() != 0):
                return 0

        nm.scan(MonitoringConfig().nmap_network, arguments='-O')

	for host in nm.all_hosts():
		if (MonitoringDatabase().is_discover_host_exist(host)):
			MonitoringDatabase().set_discover_host_os(host, nm[host])
		else:
			MonitoringDatabase().add_discover_host(nm[host], host)	

        return host

