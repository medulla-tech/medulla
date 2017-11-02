--
-- (c) 2017 Siveo, http://www.siveo.net/
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

-- -----------------------------------------------------
-- Table `rules` truncate
-- -----------------------------------------------------
truncate `xmppmaster`.`rules`;


-- -----------------------------------------------------
-- new values for table rules
-- -----------------------------------------------------


LOCK TABLES `rules` WRITE;
/*!40000 ALTER TABLE `rules` DISABLE KEYS */;
INSERT INTO `rules` VALUES (1,'user','Associate relay server based on user',3),
(2,'hostname','Associate relay server based on hostname',4),
(3,'geoposition','Select relay server based on best location',6),
(4,'subnet','Select relay server in same subnet',5),
(5,'default','Use default relay server',7),
(6,'load balancer','Choses the least used ARS',8),
(7,'orgADmach','Choses ARS based on AD OUs organised by machines ',1),
(8,'orgADuser','Choses ARS based on AD OUs organised by users',2);
/*!40000 ALTER TABLE `rules` ENABLE KEYS */;
UNLOCK TABLES;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 6;

COMMIT;
