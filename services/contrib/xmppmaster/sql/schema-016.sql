--
-- (c) 2018 Siveo, http://www.siveo.net/
--
-- $Id$
--
-- This file is part of Pulse 2, http://www.siveo.net/
--
-- Pulse 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Pulse 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Pulse 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

START TRANSACTION;

LOCK TABLES `qa_custom_command` WRITE;

INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Show process List','wmic process list brief','Get list of processes from WMI');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','View task list','tasklist','Get list of tasks');
INSERT INTO `qa_custom_command` VALUES ('allusers','linux','Show process List','ps aux','Get list of processes');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','Show process List','ps aux','Get list of processes');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Show services List','wmic service list brief','Get list of services from WMI');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','Show services List','launchctl list','Get list of services');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','View free disk space','wmic logicaldisk get FreeSpace','Get free disk space from WMI');
INSERT INTO `qa_custom_command` VALUES ('allusers','linux','View free disk space','df -h','Get free disk space');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','View free disk space','df -h','Get free disk space');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Show connected users list','wmic computersystem get username','Get list of connected users from WMI');
INSERT INTO `qa_custom_command` VALUES ('allusers','linux','Show connected users list','w','Get list of connected users');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','Show connected users list','w','Get list of connected users');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','List Network Connections','netstat -an','Get list of network connections and ports');
INSERT INTO `qa_custom_command` VALUES ('allusers','linux','List Network Connections','netstat -an','Get list of network connections and ports');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','List Network Connections','netstat -an','Get list of network connections and ports');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Show routing table','route print','View the IP routing table');
INSERT INTO `qa_custom_command` VALUES ('allusers','linux','Show routing table','netstat -rn','View the IP routing table');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','Show routing table','netstat -rn','View the IP routing table');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Show last 100 lines of agent logs','powershell.exe Get-Content  \'C:\\Program Files\\Pulse\\var\\log\\xmpp-agent.log\' -Tail 100','Get the 100 last lines of XMPP agent logs');
INSERT INTO `qa_custom_command` VALUES ('allusers','linux','Show last 100 lines of agent logs','tail -n100 /var/log/pulse/xmpp-agent.log','Get the 100 last lines of XMPP agent logs');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','Show last 100 lines of agent logs','tail -n100 \'/Library/Application Support/Pulse/var/log/xmpp-agent.log\'','Get the 100 last lines of XMPP agent logs');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Reconfigure machine agent','plugin_force_setup_agent@_@','Force the machine agent to reconfigure itself');
INSERT INTO `qa_custom_command` VALUES ('allusers','linux','Reconfigure machine agent','plugin_force_setup_agent@_@','Force the machine agent to reconfigure itself');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','Reconfigure machine agent','plugin_force_setup_agent@_@','Force the machine agent to reconfigure itself');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Disable fast startup','REG ADD \'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power\' /V HiberbootEnabled /T REG_dWORD /D 0 /F','Disable Windows 10 fast startup');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Enable fast startup','REG ADD \'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power\' /V HiberbootEnabled /T REG_dWORD /D 1 /F','Enable Windows 10 fast startup');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Restart machine agent','plugin_restartbot@_@','Restart the machine agent');
INSERT INTO `qa_custom_command` VALUES ('allusers','linux','Restart machine agent','plugin_restartbot@_@','Restart the machine agent');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','Restart machine agent','plugin_restartbot@_@','Restart the machine agent');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Download agent log to file-transfer folder','plugin_downloadfile@_@C:\\Program Files\\Pulse\\var\\log\\xmpp-agent.log','Download agent full log to file-transfer folder');
INSERT INTO `qa_custom_command` VALUES ('allusers','linux','Download agent log to file-transfer folder','plugin_downloadfile@_@/var/log/pulse/xmpp-agent.log','Download agent full log to file-transfer folder');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','Download agent log to file-transfer folder','plugin_downloadfile@_@/Library/Application Support/Pulse/var/log/xmpp-agent.log','Download agent full log to file-transfer folder');
UNLOCK TABLES;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 16;

COMMIT;
