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
/*!40000 ALTER TABLE `qa_custom_command` DISABLE KEYS */;
INSERT INTO `qa_custom_command` VALUES ('root','linux','Agent logs','tail -n50 /var/log/pulse/xmpp-agent.log','Get the 50 last lines of XMPP agent logs'),('root','macos','Agent logs','tail -n50 \'/Library/Application Support/Pulse/var/log/xmpp-agent.log\'','Get the 50 last lines of XMPP agent logs'),('root','windows','Agent logs','powershell.exe Get-Content  \'C:\\Program Files\\Pulse\\var\\log\\xmpp-agent.log\' -Tail 50','Get the 50 last lines of XMPP agent logs'),('root','linux','Connected users list','w','Get list of connected users'),('root','macos','Connected users list','w','Get list of connected users'),('root','windows','Connected users list','wmic computersystem get username','Get list of connected users from WMI'),('root','windows','Download agent log on group','plugin_downloadfile@_@C:\\Program Files\\Pulse\\var\\log\\xmpp-agent.log','download agent log'),('root','linux','Free disk space','df -h','Get free disk space'),('root','macos','Free disk space','df -h','Get free disk space'),('root','windows','Free disk space','wmic logicaldisk get FreeSpace','Get free disk space from WMI'),('root','windows','ipconfig','ipconfig /all','network informations'),('root','linux','List Network Connections','netstat -an','Get list of network connections and ports'),('root','macos','List Network Connections','netstat -an','Get list of network connections and ports'),('root','windows','List Network Connections','netstat -an','Get list of network connections and ports'),('root','linux','Process List','ps aux','Get list of processes'),('root','macos','Process List','ps aux','Get list of processes'),('root','windows','Process List','wmic process list brief','Get list of processes from WMI'),('root','linux','Routing table','netstat -rn','View the IP routing table'),('root','macos','Routing table','netstat -rn','View the IP routing table'),('root','windows','Routing table','route print','View the IP routing table'),('root','macos','Services List','launchctl list','Get list of services'),('root','windows','Services List','wmic service list brief','Get list of services from WMI'),('root','windows','Task list','tasklist','Get list of tasks');
/*!40000 ALTER TABLE `qa_custom_command` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 16;

COMMIT;

