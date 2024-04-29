--
-- (c) 2018 Siveo, http://www.siveo.net/
--
-- $Id$
--
-- This file is part of Medulla 2, http://www.siveo.net/
--
-- Medulla 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Medulla 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Medulla 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

START TRANSACTION;

LOCK TABLES `qa_custom_command` WRITE;
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Restart Medulla Agent service','powershell -command "Restart-Service medullaagent -Force"','Restart Medulla Agent windows service');
INSERT INTO `qa_custom_command` VALUES ('allusers','linux','Restart Medulla Agent service','systemctl restart medulla-agent-machine.service','Restart Medulla Agent linux service');
INSERT INTO `qa_custom_command` VALUES ('allusers','macos','Restart Medulla Agent service','launchctl kickstart -k system/net.siveo.medulla_agent','Restart Medulla Agent macos service');
UNLOCK TABLES;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 30;

COMMIT;
