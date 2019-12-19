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
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Restart Pulse Agent service','powershell -command "Restart-Service pulseagent -Force"','Restart Pulse Agent windows service');
INSERT INTO `qa_custom_command` VALUES ('allusers','linux','Restart Pulse Agent service','systemctl restart pulse-xmpp-agent-machine.service','Restart pulse-xmpp-agent-machine systemctl service');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','Restart Pulse Agent service','launchctl kickstart -k system/net.siveo.pulse_xmpp_agent','Restart net.siveo.pulse_xmpp_agent launchctl service');
UNLOCK TABLES;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 30;

COMMIT;
