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
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','VNC view primary screen','\'c:\\Program Files\\TightVNC\\tvnserver.exe\' -controlservice -shareprimary','Display primary screen');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','VNC view secondary screen','\'c:\\Program Files\\TightVNC\\tvnserver.exe\' -controlservice -sharedisplay 1','Display secondary screen');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','VNC view all screen','\'c:\\Program Files\\TightVNC\\tvnserver.exe\' -controlservice -sharefull','Display all screens');
UNLOCK TABLES;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 27;

COMMIT;
