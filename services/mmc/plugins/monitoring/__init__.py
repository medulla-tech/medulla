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

import logging
  
from pulse2.version import getVersion, getRevision # pyflakes.ignore
from mmc.core.tasks import TaskManager  
from mmc.plugins.monitoring.config import MonitoringConfig
from mmc.plugins.monitoring import mnt
# Database
from pulse2.database.monitoring import MonitoringDatabase
  
APIVERSION = "4:1:3"
NAME = "monitoring"


def getApiVersion(): return APIVERSION
def activate():
    config = MonitoringConfig(NAME)
    if config.disabled:
        logging.getLogger().warning("Plugin %s: disabled by configuration." % NAME)
        return False
    if not MonitoringDatabase().activate(config):
        logging.getLogger().warning("Plugin monitoring: an error occurred during the database initialization")
        return False
    # Add nmap network discovery task in the task manager
    if MonitoringConfig().nmap_enable == "1":
    	TaskManager().addTask("monitoring.get_task_host_os", (mnt.get_task_host_os,), cron_expression=config.nmap_task_time)
	logging.getLogger().warning("Plugin %s: NMAP enable  by configuration." % NAME)
	
    return True

def test():
  return mnt.get_task_host_os()


######################################################################################

#####################################################################################

def getMonitoringUri():
    return MonitoringConfig().monitoring_uri

def getMonitoringUsername():
	return MonitoringConfig().monitoring_username

def getMonitoringPassword():
	return MonitoringConfig().monitoring_password

def get_host_os(ip):
	return mnt.get_host_os(ip)
	
# #############################################################
# DATABASE QUERY FUNCTIONS
# #############################################################

# MONITORING DISCOVERY

def get_discover_host_all():
   return MonitoringDatabase().get_discover_host_all()

def get_discover_host_os(ip):
   return MonitoringDatabase().get_discover_host_os(ip)

def set_discover_host_os(ip, os):
   return MonitoringDatabase().set_discover_host_os(ip, os)

def add_discover_host(ip, os):
   return MonitoringDatabase().add_discover_host(os, ip)

# MONITORING ACK USER

def add_ack(username, ackid, ackmessage):
    return MonitoringDatabase().add_ack(username, ackid, ackmessage)

def get_ack(ackid):
    return MonitoringDatabase().get_ack(ackid)
